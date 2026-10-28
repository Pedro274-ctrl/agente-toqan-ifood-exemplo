"""
Gera banco SQLite com dados 100% ficticios para portfolio (LGPD safe).
"""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE vendas (
    id INTEGER PRIMARY KEY,
    produto TEXT,
    quantidade INTEGER,
    valor_unitario REAL,
    valor_total REAL,
    data TEXT,
    canal TEXT
);
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    produto TEXT,
    status TEXT,
    motivo TEXT,
    horario TEXT,
    tempo_preparo_min INTEGER,
    data TEXT
);
CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY,
    produto TEXT,
    nota INTEGER,
    comentario TEXT,
    data TEXT
);
""")

produtos = ["chopp 300ml", "chopp 500ml", "batata frita", "pastel de carne", "pastel de queijo", "hamburguer", "refrigerante", "agua"]
canais = ["ifood", "balcao", "whatsapp"]
status_list = ["entregue", "entregue", "entregue", "entregue", "cancelado"]
motivos_cancel = ["falta de entregador", "cliente nao encontrado", "restaurante sem estoque", "tempo de entrega alto", ""]
comentarios = ["Muito bom!", "Demorou", "Frio", "Excelente", "Top", "Ok"]

hoje = datetime.now()

for i in range(1, 501):
    produto = random.choice(produtos)
    qtd = random.randint(1,4)
    valor_u = random.choice([8.0, 12.0, 15.0, 22.0, 28.0, 6.0])
    valor_t = qtd * valor_u
    data = (hoje - timedelta(days=random.randint(0,30))).strftime("%Y-%m-%d")
    canal = random.choice(canais)
    cur.execute("INSERT INTO vendas (produto, quantidade, valor_unitario, valor_total, data, canal) VALUES (?,?,?,?,?,?)", (produto, qtd, valor_u, valor_t, data, canal))
    status = random.choice(status_list)
    motivo = random.choice(motivos_cancel) if status == "cancelado" else ""
    horario = f"{random.randint(11,22):02d}:{random.randint(0,59):02d}:00"
    tempo = random.randint(10, 45)
    cur.execute("INSERT INTO pedidos (produto, status, motivo, horario, tempo_preparo_min, data) VALUES (?,?,?,?,?,?)", (produto, status, motivo, horario, tempo, data))
    if random.random() > 0.3:
        nota = random.choices([5,4,3,2,1], weights=[40,30,15,10,5])[0]
        comentario = random.choice(comentarios)
        cur.execute("INSERT INTO avaliacoes (produto, nota, comentario, data) VALUES (?,?,?,?)", (produto, nota, comentario, data))

conn.commit()
conn.close()
print(f"Banco ficticio criado em {DB_PATH}")
print("500 vendas, 500 pedidos, ~350 avaliacoes - LGPD safe")