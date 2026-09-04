"""Requisito adicional 3: cancelamento de ordens."""

from decimal import Decimal

import pytest

from matching_engine.books.book import Book
from matching_engine.books.lob import LimitOrderBook


@pytest.fixture
def lob():
    return LimitOrderBook()


# --------------------------------------------------------------------------
# Caminho feliz
# --------------------------------------------------------------------------

def test_ordem_cancelada_sai_do_livro(lob, limit_buy):
    order = limit_buy(10, 100)
    lob.submit(order)
    lob.cancel_order(order.order_id)

    assert lob.bid_side.is_empty
    assert lob.best_bid is None


def test_cancelamento_limpa_os_dois_indices(lob, limit_buy):
    """O id sai tanto do indice do LOB quanto do indice do Book."""
    order = limit_buy(10, 100)
    lob.submit(order)
    lob.cancel_order(order.order_id)

    assert order.order_id not in lob.order_book
    assert order.order_id not in lob.bid_side.ids_to_orders


def test_cancela_ordem_de_venda(lob, limit_sell):
    order = limit_sell(20, 100)
    lob.submit(order)
    lob.cancel_order(order.order_id)

    assert lob.ask_side.is_empty
    assert lob.best_offer is None


def test_cancelamento_nao_afeta_as_outras_da_fila(lob, limit_sell):
    """Tirar uma ordem do meio preserva a ordem de chegada das demais."""
    a, b, c = limit_sell(10, 10), limit_sell(10, 20), limit_sell(10, 30)
    for order in (a, b, c):
        lob.submit(order)

    lob.cancel_order(b.order_id)

    assert list(lob.ask_side.levels[Decimal(10)].orders) == [a, c]


def test_cancelar_a_primeira_da_fila(lob, limit_sell):
    primeira, segunda = limit_sell(10, 100), limit_sell(10, 200)
    lob.submit(primeira)
    lob.submit(segunda)

    lob.cancel_order(primeira.order_id)

    assert lob.ask_side.levels[Decimal(10)].peek() is segunda


def test_cancelar_nao_mexe_no_outro_lado(lob, limit_buy, limit_sell):
    compra = limit_buy(10, 100)
    venda = limit_sell(20, 100)
    lob.submit(compra)
    lob.submit(venda)

    lob.cancel_order(compra.order_id)

    assert lob.bid_side.is_empty
    assert lob.best_offer == Decimal(20)


# --------------------------------------------------------------------------
# Efeito no livro
# --------------------------------------------------------------------------

def test_cancelar_a_ultima_do_nivel_apaga_o_nivel(lob, limit_buy):
    """Um nivel vazio nao pode continuar aparecendo em best_price()."""
    order = limit_buy(10, 100)
    lob.submit(order)
    lob.submit(limit_buy(9, 100))

    lob.cancel_order(order.order_id)

    assert Decimal(10) not in lob.bid_side.levels
    assert lob.best_bid == Decimal(9)


def test_nivel_sobrevive_se_ainda_tem_ordem(lob, limit_buy):
    a, b = limit_buy(10, 100), limit_buy(10, 200)
    lob.submit(a)
    lob.submit(b)

    lob.cancel_order(a.order_id)

    assert Decimal(10) in lob.bid_side.levels
    assert lob.bid_side.levels[Decimal(10)].total_quantity == Decimal(200)


def test_ordem_cancelada_nao_gera_mais_trades(lob, limit_sell, market_buy):
    """Depois de cancelada, a liquidez dela nao existe mais."""
    venda = limit_sell(10, 100)
    lob.submit(venda)
    lob.cancel_order(venda.order_id)

    assert lob.submit(market_buy(50)) == []


def test_cancelar_o_topo_move_o_melhor_preco(lob, limit_sell):
    topo = limit_sell(10, 100)
    lob.submit(topo)
    lob.submit(limit_sell(11, 100))
    assert lob.best_offer == Decimal(10)

    lob.cancel_order(topo.order_id)

    assert lob.best_offer == Decimal(11)


# --------------------------------------------------------------------------
# Erros e casos de borda
# --------------------------------------------------------------------------

def test_cancelar_id_inexistente_avisa_e_nao_quebra(lob, capsys):
    lob.cancel_order("nao-existe")

    assert "Não há ordem com ID" in capsys.readouterr().out


def test_cancelar_duas_vezes_avisa_na_segunda(lob, limit_buy, capsys):
    order = limit_buy(10, 100)
    lob.submit(order)

    lob.cancel_order(order.order_id)
    capsys.readouterr()
    lob.cancel_order(order.order_id)

    assert "Não há ordem com ID" in capsys.readouterr().out


def test_cancelar_em_livro_vazio_nao_quebra(lob, capsys):
    lob.cancel_order("qualquer-coisa")

    assert "Não há ordem com ID" in capsys.readouterr().out


def test_market_nao_pode_ser_cancelada(lob, limit_sell, market_buy, capsys):
    """Uma market nunca repousa no livro, entao nao entra no indice."""
    lob.submit(limit_sell(10, 100))
    market = market_buy(50)
    lob.submit(market)
    capsys.readouterr()

    lob.cancel_order(market.order_id)

    assert "Não há ordem com ID" in capsys.readouterr().out


def test_cancelar_ordem_parcialmente_executada(lob, limit_sell, market_buy):
    """O saldo em aberto sai do livro; o que ja foi executado permanece."""
    venda = limit_sell(10, 100)
    lob.submit(venda)
    lob.submit(market_buy(40))

    lob.cancel_order(venda.order_id)

    assert venda.filled_quantity == Decimal(40)
    assert lob.ask_side.is_empty


def test_trades_anteriores_sobrevivem_ao_cancelamento(lob, limit_sell, market_buy):
    """Cancelar nao desfaz o que ja foi negociado."""
    venda = limit_sell(10, 100)
    lob.submit(venda)
    lob.submit(market_buy(40))

    lob.cancel_order(venda.order_id)

    assert len(lob.trades) == 1
    assert lob.trades[0].quantity == Decimal(40)


# --------------------------------------------------------------------------
# Book.remove isolado
# --------------------------------------------------------------------------

def test_book_remove_encontra_a_ordem_pelo_id(limit_buy):
    """O indice ids_to_orders evita varrer os niveis atras do identificador."""
    book = Book("buy")
    order = limit_buy(10, 100)
    book.add(order)

    assert book.ids_to_orders[order.order_id] is order

    book.remove(order.order_id)

    assert book.is_empty
    assert order.order_id not in book.ids_to_orders


def test_book_remove_com_id_desconhecido_avisa(capsys):
    book = Book("buy")
    book.remove("nao-existe")

    assert "Não há ordem com ID" in capsys.readouterr().out


def test_ordem_totalmente_executada_sai_dos_indices(lob, limit_sell, market_buy, capsys):
    """Uma ordem que foi toda executada nao deve continuar indexada.

    Ela ja saiu da fila do nivel durante o matching; se o id continuar nos
    indices, os dicionarios crescem indefinidamente e um cancelamento tardio
    encontra uma entrada que nao corresponde a nada no livro.
    """
    venda = limit_sell(10, 100)
    lob.submit(venda)
    lob.submit(market_buy(100))
    capsys.readouterr()

    assert venda.status == "FILLED"
    assert venda.order_id not in lob.order_book
    assert venda.order_id not in lob.ask_side.ids_to_orders
