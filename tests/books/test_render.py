"""Visualizacao do livro (requisito adicional 1)."""

from decimal import Decimal

import pytest

from matching_engine.books.lob import LimitOrderBook


@pytest.fixture
def lob():
    return LimitOrderBook()


def test_livro_vazio_mostra_so_o_cabecalho(lob, capsys):
    capsys.readouterr()
    lob.render()
    linhas = capsys.readouterr().out.strip().splitlines()
    assert len(linhas) == 2
    assert "Ordens de Compra" in linhas[0]


def test_mostra_os_dois_lados(lob, limit_buy, limit_sell, capsys):
    lob.submit(limit_buy(10, 200))
    lob.submit(limit_sell("10.5", 100))
    capsys.readouterr()
    lob.render()
    saida = capsys.readouterr().out

    assert "200 @ 10" in saida
    assert "100 @ 10.5" in saida


def test_agrega_quantidade_por_nivel(lob, limit_buy, capsys):
    """Duas ordens no mesmo preco aparecem como uma linha somada."""
    lob.submit(limit_buy(10, 100))
    lob.submit(limit_buy(10, 200))

    capsys.readouterr()
    lob.render()
    assert "300 @ 10" in capsys.readouterr().out


def test_ordena_do_melhor_para_o_pior(lob, limit_buy, limit_sell, capsys):
    for price in ("9.99", "10", "9.98"):
        lob.submit(limit_buy(price, 100))
    for price in ("11", "10.5"):
        lob.submit(limit_sell(price, 100))

    capsys.readouterr()
    lob.render()
    linhas = capsys.readouterr().out.strip().splitlines()[2:]
    assert linhas[0].startswith("100 @ 10 ")
    assert "100 @ 10.5" in linhas[0]
    assert linhas[1].startswith("100 @ 9.99")


def test_lados_com_alturas_diferentes(lob, limit_buy, limit_sell, capsys):
    """Um lado com mais niveis que o outro nao quebra o alinhamento."""
    for price in ("10", "9.99", "9.98"):
        lob.submit(limit_buy(price, 100))
    lob.submit(limit_sell(11, 100))

    capsys.readouterr()
    lob.render()
    linhas = capsys.readouterr().out.strip().splitlines()
    assert len(linhas) == 5          # 2 de cabecalho + 3 niveis de compra


def test_reflete_o_livro_do_requisito_5(lob, limit_buy, limit_sell, capsys):
    """O livro hipotetico do enunciado."""
    lob.submit(limit_buy(10, 200))
    lob.submit(limit_buy("9.99", 100))
    lob.submit(limit_sell("10.5", 100))

    capsys.readouterr()
    lob.render()
    saida = capsys.readouterr().out
    assert "200 @ 10" in saida
    assert "100 @ 9.99" in saida
    assert "100 @ 10.5" in saida
