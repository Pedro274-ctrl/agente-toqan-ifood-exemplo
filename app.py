import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
from openai import OpenAI

load_dotenv()

app = FastAPI(
    title="Agente Toqan - Barra Space Center - RAG Exemplo",
    description="Agente de consulta ao diretório de condôminos usando OpenAI API + MySQL",
    version="1.0.0"
)

# Configuração OpenAI - chave vem do .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ConsultaRequest(BaseModel):
    pergunta: str
    usuario: str = "anonimo"

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "barra_space_center"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        port=int(os.getenv("DB_PORT", "3306"))
    )

def buscar_condominos(termo: str):
    """Busca simples no diretório - RAG básico sem vetorização ainda"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Busca parametrizada - protege SQL Injection
        query = """
            SELECT id, nome, sala, categoria, contato, visibilidade 
            FROM condominos 
            WHERE visibilidade = 'ativo' 
            AND (nome LIKE %s OR categoria LIKE %s)
            LIMIT 10
        """
        like_termo = f"%{termo}%"
        cursor.execute(query, (like_termo, like_termo))
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Exception as e:
        print(f"Erro DB: {e}")
        return []

@app.get("/")
def root():
    return {"status": "Agente Toqan Barra Space - online", "endpoint": "/consulta"}

@app.post("/consulta")
def consulta_agente(req: ConsultaRequest):
    start = time.time()
    
    if not req.pergunta or len(req.pergunta.strip()) < 3:
        raise HTTPException(status_code=400, detail="Pergunta muito curta")

    # 1. Buscar contexto no banco (RAG simples)
    # Extrai palavra-chave da pergunta para busca - versão simples
    # Em produção usaria embeddings com LlamaIndex
    palavras = req.pergunta.lower().split()
    # Pega termos relevantes (remove stopwords simples)
    stopwords = ["quais", "qual", "onde", "como", "que", "são", "estão", "no", "na", "do", "da", "de", "para", "com"]
    termos_busca = [p for p in palavras if p not in stopwords]
    termo_principal = termos_busca[0] if termos_busca else req.pergunta[:20]
    
    condominos = buscar_condominos(termo_principal)
    
    # 2. Montar contexto para LLM
    if condominos:
        contexto = "\n".join([f"- {c['nome']} - Sala {c['sala']} - Categoria {c.get('categoria','')} - Contato {c.get('contato','')}" for c in condominos])
    else:
        # Se não achou com termo, busca geral ativos
        condominos = buscar_condominos("")
        contexto = "\n".join([f"- {c['nome']} - Sala {c['sala']}" for c in condominos[:5]]) if condominos else "Nenhuma empresa encontrada no diretório ativo."

    prompt_sistema = """Você é um assistente do Barra Space Center. 
    Responda com base APENAS no contexto do diretório de empresas abaixo.
    Seja direto, liste nome, sala e contato quando disponível.
    Se não encontrar, diga que não encontrou no diretório ativo.
    Contexto:
    """ + contexto

    # 3. Chamar OpenAI API
    try:
        resposta_llm = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": req.pergunta}
            ],
            temperature=0.3,
            max_tokens=400
        )
        resposta_texto = resposta_llm.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro OpenAI: {str(e)}")

    tempo_ms = int((time.time() - start) * 1000)

    return {
        "pergunta": req.pergunta,
        "resposta": resposta_texto,
        "fontes": [f"condominos.id {c['id']}" for c in condominos[:5]],
        "tempo_ms": tempo_ms,
        "usuario": req.usuario
    }
