import pytest
from src.agent.orchestrator import processar_pergunta
@pytest.mark.asyncio
async def test_agent_fallback():
    resp = await processar_pergunta("quanto vendi ontem?")
    assert "R$" in resp or "Vendas" in resp