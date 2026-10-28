import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "database.db"

def _parse_data(data_str: str) -> str:
    hoje = datetime.now()
    data_str = (data_str or "").lower()
    if "ontem" in data_str:
        return (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    if "hoje" in data_str:
        return hoje.strftime("%Y-%m-%d")
    if "domingo" in data_str or "ultimo_domingo" in data_str:
        offset = (hoje.weekday() + 1) % 7
        if offset == 0:
            offset = 7
        return (hoje - timedelta(days=offset)).strftime("%Y-%m-%d")
    try:
        return datetime.fromisoformat(data_str).strftime("%Y-%m-%d")
    except:
        return (hoje - timedelta(days=7)).strftime("%Y-%m-%d")

def consultar_vendas_por_produto(produto: str = "todos", data_inicio: str = "7 dias atras", data_fim: str = "hoje") -> dict:
    """
    Consulta vendas por produto no periodo. Tool usada pelo LLM via Function Calling.
    """
    if not DB_PATH.exists():
        return {"erro": "Banco nao encontrado. Rode src/data/seed_ficticio.py", "qtd": 0, "total": 0}

    inicio = _parse_data(data_inicio)
    fim = _parse_data(data_fim)
    if inicio > fim:
        inicio, fim = fim, inicio

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if produto.lower() in ["todos", "tudo", "geral", ""]:
        cur.execute("SELECT COUNT(*) as qtd, COALESCE(SUM(quantidade),0), COALESCE(SUM(valor_total),0) FROM vendas WHERE data BETWEEN ? AND ?", (inicio, fim))
    else:
        cur.execute("SELECT COUNT(*) as qtd, COALESCE(SUM(quantidade),0), COALESCE(SUM(valor_total),0) FROM vendas WHERE LOWER(produto) LIKE ? AND data BETWEEN ? AND ?", (f"%{produto.lower()}%", inicio, fim))

    row = cur.fetchone()
    qtd_pedidos, qtd_itens, total = row if row else (0,0,0)
    ticket = round(total / qtd_pedidos, 2) if qtd_pedidos else 0
    conn.close()
    return {
        "produto": produto,
        "periodo": {"inicio": inicio, "fim": fim},
        "qtd_pedidos": int(qtd_pedidos),
        "qtd_itens": int(qtd_itens),
        "total": float(total),
        "ticket_medio": float(ticket)
    }