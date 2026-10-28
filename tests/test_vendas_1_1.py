from src.tools.vendas import consultar_vendas_por_produto
def test_consultar_vendas():
    r = consultar_vendas_por_produto(produto="todos")
    assert "total" in r