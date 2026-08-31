"""Testes do parser de comandos."""

from decimal import Decimal

import pytest

from matching_engine.engine import MatchingEngine


@pytest.fixture
def engine():
    return MatchingEngine()


def test_limit_tem_preco_e_quantidade(engine):
    assert engine._parse_order("limit buy 10 100") == {
        "tipo": "limit", "side": "buy", "price": Decimal(10), "qty": Decimal(100),
    }


def test_market_tem_quantidade_e_nenhum_preco(engine):
    """Em `market sell 200` o 200 e QUANTIDADE, nao preco."""
    assert engine._parse_order("market sell 200") == {
        "tipo": "market", "side": "sell", "price": None, "qty": Decimal(200),
    }


def test_aceita_preco_decimal(engine):
    assert engine._parse_order("limit buy 10.5 100")["price"] == Decimal("10.5")


@pytest.mark.parametrize("linha", [
    "market buy",
    "limit buy 10",
    "foo buy 10 100",
    "limit hold 10 100",
    "limit buy abc 100",
    "limit buy -5 100",
    "market buy 0",
    "",
])
def test_linhas_invalidas(engine, linha):
    assert engine._parse_order(linha) is None


def test_espacos_extras_sao_tolerados(engine):
    assert engine._parse_order("  limit   buy   10   100  ") == {
        "tipo": "limit", "side": "buy", "price": Decimal(10), "qty": Decimal(100),
    }


def test_maiusculas_sao_normalizadas(engine):
    assert engine._parse_order("LIMIT BUY 10 100")["tipo"] == "limit"


def test_quantidade_decimal(engine):
    assert engine._parse_order("limit buy 10 0.5")["qty"] == Decimal("0.5")


@pytest.mark.parametrize("linha", [
    "limit buy 10 100 200",     # tokens demais
    "market buy 100 200",       # market com 4 tokens
    "limit buy",                # tokens de menos
    "limit",
    "buy 10 100",               # sem tipo
    "limit buy 0 100",          # preco zero
    "limit buy 10 0",           # qty zero
    "limit buy 10 -100",        # qty negativa
    "limit buy NaN 100",
    "limit buy Infinity 100",
])
def test_mais_linhas_invalidas(engine, linha):
    assert engine._parse_order(linha) is None


def test_notacao_cientifica_e_um_preco_valido(engine):
    """1e5 e 100000 -- estranho de digitar, mas nao e invalido."""
    assert engine._parse_order("limit buy 1e5 100")["price"] == Decimal(100000)
