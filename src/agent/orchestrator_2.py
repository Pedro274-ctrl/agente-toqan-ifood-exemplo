import os
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass
from .prompt import SYSTEM_PROMPT
from ..tools.vendas import consultar_vendas_por_produto
from ..tools.cancelamentos import diagnosticar_cancelamentos
from ..tools.avaliacoes import monitorar_avaliacoes
from ..tools.gargalos import analisar_gargalos

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_vendas_por_produto",
            "description": "Consulta vendas de um produto em um periodo",
            "parameters": {
                "type": "object",
                "properties": {
                    "produto": {"type": "string", "description": "Nome do produto ou 'todos'"},
                    "data_inicio": {"type": "string"},
                    "data_fim": {"type": "string"}
                },
                "required": ["produto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "diagnosticar_cancelamentos",
            "description": "Diagnostica motivos de cancelamento",
            "parameters": {"type": "object", "properties": {"data_inicio": {"type": "string"}, "data_fim": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "monitorar_avaliacoes",
            "description": "Monitora avaliacoes",
            "parameters": {"type": "object", "properties": {"produto": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analisar_gargalos",
            "description": "Analisa gargalos operacionais",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

TOOL_MAP = {
    "consultar_vendas_por_produto": consultar_vendas_por_produto,
    "diagnosticar_cancelamentos": diagnosticar_cancelamentos,
    "monitorar_avaliacoes": monitorar_avaliacoes,
    "analisar_gargalos": analisar_gargalos
}

async def processar_pergunta(pergunta: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    # Modo com OpenAI real
    if api_key and api_key.startswith("sk-"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pergunta}
                ],
                tools=TOOLS,
                tool_choice="auto"
            )
            msg = response.choices[0].message
            if msg.tool_calls:
                tool_call = msg.tool_calls[0]
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                resultado = TOOL_MAP[func_name](**args)
                second = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": pergunta},
                        msg,
                        {"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": json.dumps(resultado, ensure_ascii=False)}
                    ]
                )
                return second.choices[0].message.content
            return msg.content
        except Exception as e:
            print(f"Erro OpenAI: {e}")

    # Fallback sem chave - para demo
    pergunta_lower = pergunta.lower()
    if any(p in pergunta_lower for p in ["venda", "vendi", "fatur", "chopp", "quanto"]):
        produto = "chopp" if "chopp" in pergunta_lower else "todos"
        data_inicio = "ontem" if "ontem" in pergunta_lower else "7 dias atras"
        r = consultar_vendas_por_produto(produto=produto, data_inicio=data_inicio, data_fim="hoje")
        return f"""Vendas - {produto} ({r['periodo']['inicio']} a {r['periodo']['fim']}):
- Pedidos: {r['qtd_pedidos']}
- Itens: {r['qtd_itens']}
- Total: R$ {r['total']:.2f}
- Ticket medio: R$ {r['ticket_medio']:.2f}
Insight: {'Acima da media' if r['total'] > 500 else 'Dentro da media'} no periodo.
Acao: Reforce estoque no pico."""
    if any(p in pergunta_lower for p in ["cancel"]):
        r = diagnosticar_cancelamentos()
        motivos_txt = ", ".join([f"{m['motivo']} ({m['qtd']})" for m in r['top_motivos']])
        return f"Cancelamentos: {r['total_cancelados']}/{r['total_pedidos']} ({r['taxa_cancelamento']}%). Top: {motivos_txt}. {r['insight']}."
    if any(p in pergunta_lower for p in ["avalia", "nota", "estrela"]):
        r = monitorar_avaliacoes()
        piores_txt = ", ".join([f"{p['produto']} ({p['media']})" for p in r['piores_pratos']])
        return f"Avaliacoes: media {r['media_geral']} em {r['total_avaliacoes']} avaliacoes. Piores: {piores_txt}. {r['alerta']}."
    if any(p in pergunta_lower for p in ["gargalo", "tempo", "preparo", "pico", "fila"]):
        r = analisar_gargalos()
        return f"Gargalos: tempo medio {r['tempo_medio_preparo_min']}min (max {r['tempo_max_preparo_min']}min). Pico as {r['horario_pico']} com {r['qtd_pedidos_pico']} pedidos. {r['diagnostico']}."
    return "Ola! Sou o agente Toqan iFood exemplo. Pergunte: 'quanto vendi ontem?', 'por que cancelamentos subiram?', 'como estao minhas avaliacoes?' ou 'qual meu gargalo hoje?'"