"""Testes do PriceLevel: prioridade por TEMPO (FIFO)."""

from decimal import Decimal

from matching_engine.books.price_level import PriceLevel


def test_ordens_saem_na_ordem_de_chegada(limit_sell):
    """Requisito adicional 2: quem chega primeiro executa primeiro."""
    level = PriceLevel()
    primeira, segunda = limit_sell(20, 100), limit_sell(20, 200)
    level.add(primeira)
    level.add(segunda)

    assert level.peek() is primeira
    assert level.popleft() is primeira
    assert level.peek() is segunda


def test_quantidade_total_soma_o_que_esta_em_aberto(limit_sell):
    level = PriceLevel()
    level.add(limit_sell(20, 100))
    level.add(limit_sell(20, 200))
    assert level.total_quantity == Decimal(300)


def test_quantidade_total_ignora_o_ja_executado(limit_sell):
    level = PriceLevel()
    order = limit_sell(20, 100)
    order.fill(Decimal(40))
    level.add(order)
    assert level.total_quantity == Decimal(60)


def test_remove_tira_ordem_do_meio_da_fila(limit_sell):
    level = PriceLevel()
    a, b, c = limit_sell(20, 10), limit_sell(20, 20), limit_sell(20, 30)
    for order in (a, b, c):
        level.add(order)

    level.remove(b)
    assert list(level.orders) == [a, c]


def test_nivel_vazio(limit_sell):
    level = PriceLevel()
    assert level.is_empty
    level.add(limit_sell(20, 100))
    assert not level.is_empty
