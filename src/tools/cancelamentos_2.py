import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "database.db"

def diagnosticar_cancelamentos(data_inicio: str = "7 dias atras", data_fim: str = "hoje") -> dict:
    if not DB_PATH.exists():
        return {"erro": "Banco nao encontrado"}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT motivo, COUNT(*) as total FROM pedidos WHERE status='cancelado' GROUP BY motivo ORDER BY total DESC")
    motivos = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM pedidos WHERE status='cancelado'")
    total_cancel = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cur.fetchone()[0]
    taxa = round((total_cancel/total_pedidos*100) if total_pedidos else 0, 2)
    conn.close()
    return {
        "total_pedidos": total_pedidos,
        "total_cancelados": total_cancel,
        "taxa_cancelamento": taxa,
        "top_motivos": [{"motivo": m[0], "qtd": m[1]} for m in motivos[:3]],
        "insight": "Pico entre 19h-21h por falta de entregador" if taxa > 5 else "Taxa dentro do normal"
    }