"""Casos de borda do cruzamento de ordens."""

from decimal import Decimal

import pytest

from matching_engine.books.lob import LimitOrderBook


@pytest.fixture
def lob():
    return LimitOrderBook()


# --------------------------------------------------------------------------
# Quantidades
# --------------------------------------------------------------------------

def test_quantidades_exatamente_iguais_zeram_as_duas(lob, limit_sell, limit_buy):
    venda, compra = limit_sell(10, 100), limit_buy(10, 100)
    lob.submit(venda)
    lob.submit(compra)

    assert venda.status == "FILLED"
    assert compra.status == "FILLED"
    assert lob.bid_side.is_empty and lob.ask_side.is_empty


def test_agressora_menor_que_passiva(lob, limit_sell, limit_buy):
    venda = limit_sell(10, 100)
    lob.submit(venda)
    lob.submit(limit_buy(10, 30))

    assert venda.remaining_quantity == Decimal(70)
    assert venda.status == "PARTIALLY_FILLED"
    assert lob.best_offer == Decimal(10)


def test_agressora_maior_consome_varias_passivas(lob, limit_sell, market_buy):
    a, b, c = limit_sell(10, 30), limit_sell(10, 30), limit_sell(10, 30)
    for o in (a, b, c):
        lob.submit(o)
    trades = lob.submit(market_buy(75))

    assert [t.quantity for t in trades] == [Decimal(30), Decimal(30), Decimal(15)]
    assert c.remaining_quantity == Decimal(15)


def test_quantidade_fracionaria(lob, limit_sell, limit_buy):
    lob.submit(limit_sell("10.5", "0.5"))
    trades = lob.submit(limit_buy("10.5", "0.3"))

    assert trades[0].quantity == Decimal("0.3")
    assert lob.ask_side.levels[Decimal("10.5")].total_quantity == Decimal("0.2")


# --------------------------------------------------------------------------
# Precos
# --------------------------------------------------------------------------

def test_precos_decimais_do_enunciado(lob, limit_buy):
    """9.99, 10 e 10.1 precisam ser tres niveis distintos."""
    for price in ("9.99", "10", "10.1"):
        lob.submit(limit_buy(price, 100))

    assert lob.bid_side.sorted_prices() == [
        Decimal("10.1"), Decimal("10"), Decimal("9.99"),
    ]


def test_precisao_decimal_nao_duplica_nivel(lob, limit_buy):
    """Em float, 0.1+0.2 != 0.3; com Decimal os precos batem."""
    lob.submit(limit_buy("0.3", 100))
    lob.submit(limit_buy(Decimal("0.1") + Decimal("0.2"), 100))

    assert len(lob.bid_side.levels) == 1


def test_compra_cruza_ate_o_proprio_limite(lob, limit_sell, limit_buy):
    lob.submit(limit_sell(10, 50))
    lob.submit(limit_sell(11, 50))
    lob.submit(limit_sell(12, 50))
    trades = lob.submit(limit_buy(11, 200))

    assert [t.price for t in trades] == [Decimal(10), Decimal(11)]
    assert lob.best_offer == Decimal(12)
    assert lob.best_bid == Decimal(11)


def test_venda_cruza_ate_o_proprio_limite(lob, limit_buy, limit_sell):
    lob.submit(limit_buy(12, 50))
    lob.submit(limit_buy(11, 50))
    lob.submit(limit_buy(10, 50))
    trades = lob.submit(limit_sell(11, 200))

    assert [t.price for t in trades] == [Decimal(12), Decimal(11)]
    assert lob.best_bid == Decimal(10)


def test_preco_exatamente_igual_cruza(lob, limit_sell, limit_buy):
    """A comparacao e <= e >=, nao < e >."""
    lob.submit(limit_sell(10, 100))
    assert lob.submit(limit_buy(10, 100)) != []


def test_um_centavo_abaixo_nao_cruza(lob, limit_sell, limit_buy):
    lob.submit(limit_sell(10, 100))
    assert lob.submit(limit_buy("9.99", 100)) == []


# --------------------------------------------------------------------------
# Invariantes
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sequencia", [
    [("sell", 10, 50), ("buy", 12, 100)],
    [("buy", 12, 100), ("sell", 10, 50)],
    [("sell", 10, 50), ("sell", 11, 50), ("buy", 15, 200)],
    [("buy", 10, 50), ("buy", 11, 50), ("sell", 5, 200)],
])
def test_livro_nunca_cruzado(lob, limit_buy, limit_sell, sequencia):
    """best_bid < best_offer depois de qualquer sequencia."""
    for side, price, qty in sequencia:
        lob.submit(limit_buy(price, qty) if side == "buy" else limit_sell(price, qty))

    if lob.best_bid is not None and lob.best_offer is not None:
        assert lob.best_bid < lob.best_offer


def test_quantidade_e_conservada(lob, limit_sell, limit_buy):
    """O que foi executado sai do livro; nada some nem aparece."""
    venda = limit_sell(10, 100)
    lob.submit(venda)
    compra = limit_buy(10, 60)
    lob.submit(compra)

    executado = sum(t.quantity for t in lob.trades)
    assert executado == Decimal(60)
    assert venda.filled_quantity == compra.filled_quantity == Decimal(60)
    assert lob.ask_side.levels[Decimal(10)].total_quantity == Decimal(40)


def test_todo_trade_tem_duas_contrapartes(lob, limit_sell, market_buy):
    lob.submit(limit_sell(10, 50))
    lob.submit(limit_sell(11, 50))
    trades = lob.submit(market_buy(100))

    for t in trades:
        assert t.aggressor_order_id != t.resting_order_id
        assert t.quantity > 0


# --------------------------------------------------------------------------
# Livro vazio e casos degenerados
# --------------------------------------------------------------------------

def test_market_em_livro_vazio(lob, market_buy):
    assert lob.submit(market_buy(100)) == []
    assert lob.best_bid is None and lob.best_offer is None


def test_market_cruza_so_o_lado_oposto(lob, limit_buy, market_buy):
    """Uma compra nao cruza com outra compra."""
    lob.submit(limit_buy(10, 100))
    assert lob.submit(market_buy(50)) == []


def test_limit_nao_cruza_com_o_proprio_lado(lob, limit_sell):
    lob.submit(limit_sell(10, 100))
    assert lob.submit(limit_sell(9, 100)) == []
    assert len(lob.ask_side.levels) == 2


def test_historico_acumula_todos_os_trades(lob, limit_sell, market_buy):
    lob.submit(limit_sell(10, 50))
    lob.submit(limit_sell(11, 50))
    lob.submit(market_buy(30))
    lob.submit(market_buy(30))

    assert len(lob.trades) == 3
    assert sum(t.quantity for t in lob.trades) == Decimal(60)
