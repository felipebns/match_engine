"""Prioridade preco-tempo sob varios cenarios (requisito adicional 2)."""

from decimal import Decimal

import pytest

from matching_engine.books.lob import LimitOrderBook


@pytest.fixture
def lob():
    return LimitOrderBook()


def test_fila_de_cinco_ordens_e_consumida_em_ordem(lob, limit_sell, market_buy):
    ordens = [limit_sell(10, 20) for _ in range(5)]
    for o in ordens:
        lob.submit(o)

    lob.submit(market_buy(50))

    assert [o.status for o in ordens] == [
        "FILLED", "FILLED", "PARTIALLY_FILLED", "NEW", "NEW",
    ]


def test_ordem_parcial_mantem_a_primeira_posicao(lob, limit_sell, market_buy):
    """Quem foi parcialmente executada nao vai para o fim da fila."""
    primeira, segunda = limit_sell(10, 100), limit_sell(10, 100)
    lob.submit(primeira)
    lob.submit(segunda)

    lob.submit(market_buy(40))
    assert lob.ask_side.levels[Decimal(10)].peek() is primeira

    lob.submit(market_buy(60))
    assert primeira.status == "FILLED"
    assert segunda.status == "NEW"


def test_preco_tem_precedencia_sobre_tempo(lob, limit_sell, market_buy):
    """Uma ordem melhor executa antes, mesmo tendo chegado depois."""
    cara = limit_sell(11, 100)
    barata = limit_sell(10, 100)
    lob.submit(cara)
    lob.submit(barata)

    trades = lob.submit(market_buy(50))
    assert trades[0].price == Decimal(10)
    assert barata.status == "PARTIALLY_FILLED"
    assert cara.status == "NEW"


def test_ordens_intercaladas_entre_niveis(lob, limit_sell, market_buy):
    a10, a11, b10, b11 = (
        limit_sell(10, 30), limit_sell(11, 30),
        limit_sell(10, 30), limit_sell(11, 30),
    )
    for o in (a10, a11, b10, b11):
        lob.submit(o)

    lob.submit(market_buy(90))

    # nivel 10 inteiro primeiro (a10, b10), depois o 11 comeca por a11
    assert [o.status for o in (a10, b10, a11, b11)] == [
        "FILLED", "FILLED", "FILLED", "NEW",
    ]


def test_bid_mais_alto_executa_primeiro(lob, limit_buy, market_sell):
    baixo, alto = limit_buy(9, 100), limit_buy(10, 100)
    lob.submit(baixo)
    lob.submit(alto)

    trades = lob.submit(market_sell(50))
    assert trades[0].price == Decimal(10)
    assert alto.status == "PARTIALLY_FILLED"
    assert baixo.status == "NEW"
