"""Testes da Order: estado e ciclo de vida."""

from decimal import Decimal


def test_ordem_nova_comeca_sem_execucao(limit_buy):
    order = limit_buy(10, 100)
    assert order.remaining_quantity == Decimal(100)
    assert order.status == "NEW"
    assert order.is_active


def test_fill_parcial_atualiza_status(limit_buy):
    order = limit_buy(10, 100)
    order.fill(Decimal(30))
    assert order.remaining_quantity == Decimal(70)
    assert order.status == "PARTIALLY_FILLED"
    assert order.is_active


def test_fill_total_marca_filled(limit_buy):
    order = limit_buy(10, 100)
    order.fill(Decimal(100))
    assert order.remaining_quantity == Decimal(0)
    assert order.status == "FILLED"
    assert not order.is_active


def test_ordem_cancelada_fica_inativa(limit_buy):
    order = limit_buy(10, 100)
    order.cancel()
    assert order.status == "CANCELLED"
    assert not order.is_active


def test_market_nao_tem_preco(market_buy):
    assert market_buy(150).price is None


def test_lado_oposto(limit_buy, limit_sell):
    assert limit_buy(10, 100).opposite_side == "sell"
    assert limit_sell(10, 100).opposite_side == "buy"


def test_ids_sao_unicos(limit_buy):
    assert limit_buy(10, 100).order_id != limit_buy(10, 100).order_id
