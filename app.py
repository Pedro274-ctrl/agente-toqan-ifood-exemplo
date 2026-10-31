import os
import re
import json
import time
import logging
import unicodedata
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import mysql.connector
from openai import OpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("agente-toqan")

app = FastAPI(
    title="Agente Toqan - Barra Space Center - RAG Exemplo",
    description="Agente de consulta ao diretório de condôminos usando OpenAI API + MySQL",
    version="1.1.0"
)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TERMOS = 5
MAX_RESULTADOS = 10

_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Cria o cliente sob demanda, para a API subir mesmo sem a chave configurada."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada no .env")
        _client = OpenAI(api_key=api_key)
    return _client


class ConsultaRequest(BaseModel):
    pergunta: str = Field(..., min_length=3, max_length=500)
    usuario: str = Field(default="anonimo", max_length=255)


class Filtros(BaseModel):
    termos: List[str] = []
    categoria: Optional[str] = None
    origem: str = "llm"


# ---------------------------------------------------------------------------
# 1. Extração de filtros (intenção) a partir da pergunta
# ---------------------------------------------------------------------------

PROMPT_EXTRACAO = """Você extrai filtros de busca para o diretório de empresas do Barra Space Center.
A tabela tem as colunas: nome (nome da empresa) e categoria (ex.: Tecnologia, Consultoria, Jurídico).
Leia a pergunta e responda SOMENTE com um JSON neste formato:
{"categoria": "<ramo de atuação no singular, com inicial maiúscula, ou null>",
 "termos": ["<nomes de empresas ou palavras-chave relevantes>"]}
Regras:
- Não inclua palavras genéricas como empresa, empresas, ativas, sala, contato, Barra Space.
- Se a pergunta citar uma empresa pelo nome, coloque o nome em "termos".
- Se não houver filtro claro, use {"categoria": null, "termos": []}."""

STOPWORDS = {
    "quais", "qual", "onde", "como", "que", "quem", "são", "sao", "estão", "estao", "está", "esta",
    "o", "a", "os", "as", "um", "uma", "no", "na", "nos", "nas", "do", "da", "dos", "das", "de",
    "em", "para", "com", "por", "e", "me", "mostra", "mostre", "liste", "listar", "tem", "existe",
    "existem", "empresa", "empresas", "ativa", "ativas", "ativo", "ativos", "sala", "salas",
    "contato", "contatos", "barra", "space", "center", "aqui", "prédio", "predio",
}


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação (corrige casos como 'space?')."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^\w\s]", " ", texto)


def limpar_termos(termos: List[str]) -> List[str]:
    limpos = []
    for t in termos:
        if not isinstance(t, str):
            continue
        t = t.strip()[:50]
        if len(t) >= 2 and normalizar(t).strip() not in STOPWORDS and t not in limpos:
            limpos.append(t)
    return limpos[:MAX_TERMOS]


def extrair_filtros_local(pergunta: str) -> Filtros:
    """Fallback sem LLM: usa TODOS os termos relevantes, não só o primeiro."""
    palavras = normalizar(pergunta).split()
    termos = [p for p in palavras if p not in STOPWORDS and len(p) >= 3]
    return Filtros(termos=limpar_termos(termos), categoria=None, origem="local")


def extrair_filtros(pergunta: str) -> Filtros:
    """Usa o LLM com saída JSON para entender a intenção; cai no fallback local se falhar."""
    try:
        resposta = get_openai_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": PROMPT_EXTRACAO},
                {"role": "user", "content": pergunta},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=150,
        )
        dados = json.loads(resposta.choices[0].message.content or "{}")
        categoria = dados.get("categoria")
        categoria = categoria.strip()[:100] if isinstance(categoria, str) and categoria.strip() else None
        termos = dados.get("termos") if isinstance(dados.get("termos"), list) else []
        return Filtros(termos=limpar_termos(termos), categoria=categoria, origem="llm")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Falha na extração via LLM, usando fallback local: %s", e)
        return extrair_filtros_local(pergunta)


# ---------------------------------------------------------------------------
# 2. Recuperação no banco (RAG simples, sem vetorização ainda)
# ---------------------------------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "barra_space_center"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        port=int(os.getenv("DB_PORT", "3306")),
    )


def montar_query(filtros: Filtros):
    """Monta a consulta parametrizada: categoria OU qualquer termo no nome/categoria."""
    condicoes, params = [], []
    if filtros.categoria:
        condicoes.append("categoria LIKE %s")
        params.append(f"%{filtros.categoria}%")
    for termo in filtros.termos:
        condicoes.append("(nome LIKE %s OR categoria LIKE %s)")
        params.extend([f"%{termo}%", f"%{termo}%"])

    query = """
        SELECT id, nome, sala, categoria, contato
        FROM condominos
        WHERE visibilidade = 'ativo'
    """
    if condicoes:
        query += " AND (" + " OR ".join(condicoes) + ")"
    query += f" ORDER BY nome LIMIT {MAX_RESULTADOS}"
    return query, tuple(params)


def buscar_condominos(filtros: Filtros) -> List[dict]:
    query, params = montar_query(filtros)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except mysql.connector.Error as e:
        logger.error("Erro no banco: %s", e)
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


# ---------------------------------------------------------------------------
# 3. Geração da resposta
# ---------------------------------------------------------------------------

def montar_contexto(condominos: List[dict]) -> str:
    if not condominos:
        return "Nenhuma empresa do diretório ativo corresponde à pergunta."
    return "\n".join(
        f"- {c['nome']} | Sala {c.get('sala') or '-'} | Categoria {c.get('categoria') or '-'} | Contato {c.get('contato') or '-'}"
        for c in condominos
    )


def gerar_resposta(pergunta: str, contexto: str) -> str:
    prompt_sistema = (
        "Você é o assistente do Barra Space Center.\n"
        "Responda em português, com base APENAS no contexto do diretório abaixo.\n"
        "Seja direto: liste nome, sala e contato quando disponível.\n"
        "Se o contexto não tiver a resposta, diga que não encontrou no diretório ativo. Não invente empresas.\n"
        "Contexto:\n" + contexto
    )
    try:
        resposta = get_openai_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": pergunta},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return resposta.choices[0].message.content
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro na OpenAI API: %s", e)
        raise HTTPException(status_code=502, detail="Falha ao gerar resposta com o modelo")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "Agente Toqan Barra Space - online", "endpoint": "/consulta"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/consulta")
def consulta_agente(req: ConsultaRequest):
    start = time.time()
    pergunta = req.pergunta.strip()
    if len(pergunta) < 3:
        raise HTTPException(status_code=400, detail="Pergunta muito curta")

    # 1. Entender a intenção (LLM com saída JSON, fallback local)
    filtros = extrair_filtros(pergunta)

    # 2. Recuperar contexto no banco
    condominos = buscar_condominos(filtros)

    # 3. Gerar resposta fundamentada apenas no contexto recuperado
    resposta_texto = gerar_resposta(pergunta, montar_contexto(condominos))

    tempo_ms = int((time.time() - start) * 1000)
    logger.info("consulta usuario=%s filtros=%s resultados=%d tempo_ms=%d",
                req.usuario, filtros.model_dump(), len(condominos), tempo_ms)

    return {
        "pergunta": pergunta,
        "resposta": resposta_texto,
        "filtros": filtros.model_dump(),
        "fontes": [f"condominos.id {c['id']}" for c in condominos],
        "tempo_ms": tempo_ms,
        "usuario": req.usuario,
    }
