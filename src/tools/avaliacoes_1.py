import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "data" / "database.db"

def monitorar_avaliacoes(produto: str = "") -> dict:
    if not DB_PATH.exists():
        return {"erro": "Banco nao encontrado"}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT AVG(nota), COUNT(*) FROM avaliacoes")
    media, total = cur.fetchone()
    cur.execute("SELECT produto, AVG(nota) as media, COUNT(*) FROM avaliacoes GROUP BY produto ORDER BY media ASC LIMIT 3")
    piores = cur.fetchall()
    conn.close()
    return {
        "media_geral": round(media or 0, 2),
        "total_avaliacoes": total,
        "piores_pratos": [{"produto": p[0], "media": round(p[1],2), "qtd": p[2]} for p in piores],
        "alerta": f"Atencao ao {piores[0][0]} com nota {round(piores[0][1],2)}" if piores else "Sem alertas"
    }