"""Testes do agente sem rede e sem banco: OpenAI e MySQL são simulados."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app as agente

EMPRESAS = [
    {"id": 1, "nome": "Alfa Tech", "sala": "101", "categoria": "Tecnologia", "contato": "alfa@ex.com"},
    {"id": 2, "nome": "Beta Sistemas", "sala": "205", "categoria": "Tecnologia", "contato": "beta@ex.com"},
]


class FakeOpenAI:
    """Simula o cliente: 1ª chamada devolve filtros JSON, 2ª devolve texto."""

    def __init__(self, filtros=None, texto="Resposta do modelo", falhar=False):
        self.filtros, self.texto, self.falhar = filtros or {}, texto, falhar
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        if self.falhar:
            raise RuntimeError("API fora do ar")
        if kwargs.get("response_format"):
            conteudo = json.dumps(self.filtros)
        else:
            conteudo = self.texto
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=conteudo))])


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(agente, "AGENT_API_TOKEN", None)
    monkeypatch.setattr(agente, "buscar_condominos", lambda f: EMPRESAS if (f.categoria or f.termos) else [])
    return TestClient(agente.app)


def usar_llm(monkeypatch, fake):
    monkeypatch.setattr(agente, "get_openai_client", lambda: fake)


# --- Consulta parametrizada e regras de segurança -------------------------

def test_query_so_ativos_e_parametrizada():
    query, params = agente.montar_query(agente.Filtros(categoria="Tecnologia", termos=["alfa"]))
    assert "visibilidade = 'ativo'" in query
    assert "Tecnologia" not in query and "alfa" not in query  # valores só nos parâmetros
    assert params[-1] == agente.MAX_RESULTADOS


def test_sem_filtro_nao_consulta_banco():
    query, params = agente.montar_query(agente.Filtros())
    assert query is None and params == ()


def test_curinga_do_usuario_e_escapado():
    _, params = agente.montar_query(agente.Filtros(termos=["%"]))
    assert params[0] == "%!%%"


def test_sql_injection_vira_texto_literal():
    malicioso = "x' OR '1'='1"
    query, params = agente.montar_query(agente.Filtros(termos=[malicioso]))
    assert malicioso not in query
    assert f"%{malicioso}%" in params


# --- Fallbacks -----------------------------------------------------------

def test_fallback_local_usa_todos_os_termos():
    f = agente.extrair_filtros_local("Quais empresas de tecnologia e jurídico estão ativas?")
    assert f.origem == "local"
    assert f.termos == ["tecnologia", "juridico"]


def test_api_fora_do_ar_continua_respondendo(client, monkeypatch):
    usar_llm(monkeypatch, FakeOpenAI(falhar=True))
    r = client.post("/consulta", json={"pergunta": "empresas de tecnologia"})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["filtros"]["origem"] == "local"
    assert corpo["origem_resposta"] == "local"
    assert "Alfa Tech" in corpo["resposta"]


def test_sem_chave_openai_usa_fallback(client, monkeypatch):
    usar_llm(monkeypatch, None)
    r = client.post("/consulta", json={"pergunta": "empresas de tecnologia"})
    assert r.status_code == 200 and r.json()["origem_resposta"] == "local"


def test_json_invalido_do_modelo_cai_no_fallback(monkeypatch):
    fake = FakeOpenAI()
    fake.chat.completions.create = lambda **k: SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="isso não é json"))])
    usar_llm(monkeypatch, fake)
    assert agente.extrair_filtros("empresas de tecnologia").origem == "local"


# --- Fluxo completo com LLM ----------------------------------------------

def test_fluxo_llm_devolve_fontes(client, monkeypatch):
    usar_llm(monkeypatch, FakeOpenAI(filtros={"categoria": "Tecnologia", "termos": []}))
    r = client.post("/consulta", json={"pergunta": "Quais empresas de tecnologia estão ativas?"})
    corpo = r.json()
    assert corpo["filtros"] == {"termos": [], "categoria": "Tecnologia", "origem": "llm"}
    assert [f["id"] for f in corpo["fontes"]] == [1, 2]
    assert corpo["origem_resposta"] == "llm"


def test_pergunta_sem_filtro_pede_esclarecimento(client, monkeypatch):
    usar_llm(monkeypatch, None)
    r = client.post("/consulta", json={"pergunta": "oi, tudo bem?"})
    assert r.json()["fontes"] == []
    assert "Não entendi" in r.json()["resposta"]


# --- Autenticação --------------------------------------------------------

def test_token_obrigatorio_quando_configurado(client, monkeypatch):
    monkeypatch.setattr(agente, "AGENT_API_TOKEN", "segredo")
    usar_llm(monkeypatch, None)
    assert client.post("/consulta", json={"pergunta": "tecnologia"}).status_code == 401
    ok = client.post("/consulta", json={"pergunta": "tecnologia"}, headers={"X-API-Key": "segredo"})
    assert ok.status_code == 200