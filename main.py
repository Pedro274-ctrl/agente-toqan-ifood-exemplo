from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.orchestrator import processar_pergunta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="agente-toqan-ifood-exemplo",
    description="Agente Toqan iFood com Function Calling - Exemplo de Portfolio",
    version="0.1.0"
)

class PerguntaRequest(BaseModel):
    pergunta: str

class RespostaResponse(BaseModel):
    resposta: str
    agente: str = "toqan-ifood-exemplo"

@app.get("/")
def root():
    return {
        "message": "Agente Toqan iFood - Exemplo",
        "docs": "/docs",
        "exemplos": [
            "quanto vendi de chopp ontem?",
            "por que meus cancelamentos subiram?",
            "como estao minhas avaliacoes?",
            "qual meu gargalo hoje?"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok", "agent": "toqan-ifood-exemplo", "toqan": "simulado"}

@app.post("/chat", response_model=RespostaResponse)
async def chat(req: PerguntaRequest):
    resposta = await processar_pergunta(req.pergunta)
    return {"resposta": resposta, "agente": "toqan-ifood-exemplo"}