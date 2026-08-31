"""Testes da agregacao de trades para exibicao."""

from decimal import Decimal

from matching_engine.books.lob import LimitOrderBook
from matching_engine.orders.trade import Trade


def trade(price, qty):
    return Trade(Decimal(str(price)), Decimal(str(qty)), "agressora", "passiva")


def test_mesmo_preco_vira_uma_linha():
    """Formato do enunciado: duas execucoes a 20 saem como uma linha de 150."""
    agregados = LimitOrderBook.aggregate([trade(20, 100), trade(20, 50)])
    assert [str(t) for t in agregados] == ["Trade, price: 20, qty: 150"]


def test_precos_diferentes_ficam_separados():
    """O preco exibido precisa ser um preco de execucao real."""
    agregados = LimitOrderBook.aggregate([trade(20, 100), trade(21, 50)])
    assert [str(t) for t in agregados] == [
        "Trade, price: 20, qty: 100",
        "Trade, price: 21, qty: 50",
    ]


def test_agrega_apenas_execucoes_consecutivas():
    agregados = LimitOrderBook.aggregate([trade(20, 10), trade(21, 5), trade(20, 30)])
    assert [(t.price, t.quantity) for t in agregados] == [
        (Decimal(20), Decimal(10)),
        (Decimal(21), Decimal(5)),
        (Decimal(20), Decimal(30)),
    ]


def test_lista_vazia():
    assert LimitOrderBook.aggregate([]) == []


def test_nao_altera_os_trades_originais():
    originais = [trade(20, 100), trade(20, 50)]
    LimitOrderBook.aggregate(originais)
    assert [t.quantity for t in originais] == [Decimal(100), Decimal(50)]
