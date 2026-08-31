from decimal import Decimal

import pytest

from matching_engine.orders.order import Order


@pytest.fixture
def limit_buy():
    """Fabrica de ordens limit de compra."""
    return lambda price, qty: Order("buy", "limit", Decimal(str(qty)), Decimal(str(price)))


@pytest.fixture
def limit_sell():
    """Fabrica de ordens limit de venda."""
    return lambda price, qty: Order("sell", "limit", Decimal(str(qty)), Decimal(str(price)))


@pytest.fixture
def market_buy():
    """Fabrica de ordens market de compra."""
    return lambda qty: Order("buy", "market", Decimal(str(qty)))


@pytest.fixture
def market_sell():
    """Fabrica de ordens market de venda."""
    return lambda qty: Order("sell", "market", Decimal(str(qty)))
