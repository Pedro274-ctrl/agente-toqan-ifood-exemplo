import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "data" / "database.db"

def analisar_gargalos() -> dict:
    if not DB_PATH.exists():
        return {"erro": "Banco nao encontrado"}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT AVG(tempo_preparo_min), MAX(tempo_preparo_min) FROM pedidos WHERE status!='cancelado'")
    media_prep, max_prep = cur.fetchone()
    cur.execute("SELECT strftime('%H', horario) as hora, COUNT(*) FROM pedidos GROUP BY hora ORDER BY COUNT(*) DESC LIMIT 1")
    pico = cur.fetchone()
    conn.close()
    return {
        "tempo_medio_preparo_min": round(media_prep or 0, 1),
        "tempo_max_preparo_min": max_prep or 0,
        "horario_pico": f"{pico[0]}h" if pico else "19h",
        "qtd_pedidos_pico": pico[1] if pico else 0,
        "diagnostico": "Gargalo na cozinha no pico" if (media_prep or 0) > 25 else "Operacao fluindo bem"
    }