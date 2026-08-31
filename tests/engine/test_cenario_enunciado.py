"""O cenario de exemplo do enunciado, ponta a ponta."""

from decimal import Decimal

import pytest

from matching_engine.engine import MatchingEngine


@pytest.fixture
def engine():
    return MatchingEngine()


def submit(engine, linha):
    parsed = engine._parse_order(linha)
    from matching_engine.orders.order import Order
    order = Order(parsed["side"], parsed["tipo"], parsed["qty"], parsed["price"])
    return engine.lob.submit(order)


def test_cenario_completo(engine):
    """
    >>> limit buy 10 100
    >>> limit sell 20 100
    >>> limit sell 20 200
    >>> market buy 150   -> Trade, price: 20, qty: 150
    >>> market buy 200   -> Trade, price: 20, qty: 150
    >>> market sell 200  -> Trade, price: 10, qty: 100
    """
    assert submit(engine, "limit buy 10 100") == []
    assert submit(engine, "limit sell 20 100") == []
    assert submit(engine, "limit sell 20 200") == []

    # Internamente sao DUAS execucoes (100 + 50), contra duas ordens distintas
    # no mesmo preco; na exibicao elas sao agregadas numa linha so.
    trades = submit(engine, "market buy 150")
    assert [(t.price, t.quantity) for t in trades] == [
        (Decimal(20), Decimal(100)),
        (Decimal(20), Decimal(50)),
    ]
    assert [str(t) for t in engine.lob.aggregate(trades)] == [
        "Trade, price: 20, qty: 150",
    ]

    # restam 150 no ask; a market pede 200 e leva so o que ha
    trades = submit(engine, "market buy 200")
    assert [(t.price, t.quantity) for t in trades] == [(Decimal(20), Decimal(150))]

    # ask vazio; a venda cruza contra o bid de 10
    trades = submit(engine, "market sell 200")
    assert [(t.price, t.quantity) for t in trades] == [(Decimal(10), Decimal(100))]

    # livro vazio no fim
    assert engine.lob.bid_side.is_empty
    assert engine.lob.ask_side.is_empty
