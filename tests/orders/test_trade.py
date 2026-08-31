"""Testes do Trade: formato de saida e imutabilidade."""

from decimal import Decimal

import pytest
from dataclasses import FrozenInstanceError

from matching_engine.orders.trade import Trade


def test_formato_exigido_pelo_enunciado():
    trade = Trade(Decimal(20), Decimal(150), "order-1", "order-2")
    assert str(trade) == "Trade, price: 20, qty: 150"


def test_trade_e_imutavel():
    trade = Trade(Decimal(20), Decimal(150), "order-1", "order-2")
    with pytest.raises(FrozenInstanceError):
        trade.price = Decimal(99)


def test_trades_iguais_comparam_iguais():
    a = Trade(Decimal(20), Decimal(150), "order-1", "order-2")
    b = Trade(Decimal(20), Decimal(150), "order-1", "order-2")
    assert a == b
