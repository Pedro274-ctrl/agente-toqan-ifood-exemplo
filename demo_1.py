"""
demo.py - Simula 5 perguntas reais do dono de restaurante iFood
Usa o mesmo orquestrador do agente Toqan, sem precisar de chave OpenAI
Ideal para gravar GIF de demo e colocar no README.md
"""
import asyncio
from src.agent.orchestrator import processar_pergunta

perguntas = [
    "quanto vendi de chopp ontem?",
    "por que meus cancelamentos subiram essa semana?",
    "como estao minhas avaliacoes?",
    "qual meu gargalo operacional hoje?",
    "quanto vendi no ultimo domingo?"
]

async def main():
    print("🤖 Agente Toqan iFood - DEMO")
    print("="*60)
    print("Modo: fallback (sem OPENAI_API_KEY) - pronto para recrutador testar")
    print("="*60 + "\n")
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n[{i}/5] 👨‍🍳 Dono: \"{pergunta}\"")
        print("-"*60)
        resposta = await processar_pergunta(pergunta)
        print(f"🤖 Agente Toqan: {resposta}")
        print()

if __name__ == "__main__":
    asyncio.run(main())