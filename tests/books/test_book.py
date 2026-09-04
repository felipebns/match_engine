"""Testes do Book: prioridade por PRECO."""

from decimal import Decimal

from matching_engine.books.book import Book


def test_compra_prioriza_maior_preco(limit_buy):
    book = Book("buy")
    for price in (10, 9.99, 10.5):
        book.add(limit_buy(price, 100))

    assert book.best_price() == Decimal("10.5")
    assert book.sorted_prices() == [Decimal("10.5"), Decimal("10"), Decimal("9.99")]


def test_venda_prioriza_menor_preco(limit_sell):
    book = Book("sell")
    for price in (10.5, 10, 11):
        book.add(limit_sell(price, 100))

    assert book.best_price() == Decimal("10")
    assert book.sorted_prices() == [Decimal("10"), Decimal("10.5"), Decimal("11")]


def test_ordens_no_mesmo_preco_dividem_o_nivel(limit_buy):
    book = Book("buy")
    book.add(limit_buy(10, 100))
    book.add(limit_buy(10, 200))

    assert len(book.levels) == 1
    assert book.levels[Decimal(10)].total_quantity == Decimal(300)


def test_nivel_vazio_e_descartado(limit_buy):
    book = Book("buy")
    order = limit_buy(10, 100)
    book.add(order)
    book.remove(order.order_id)

    assert book.is_empty
    assert book.best_price() is None


def test_livro_vazio_nao_tem_melhor_preco():
    assert Book("buy").best_price() is None


def test_nivel_vazio_nao_vira_melhor_preco(limit_sell):
    """Um nivel sem ordens nao pode ser devolvido por best_price().

    Se ficasse no dicionario, o livro anunciaria um preco onde nao ha nada
    para negociar -- e o matching tentaria cruzar contra uma fila vazia.
    """
    book = Book("sell")
    order = limit_sell(10, 100)
    book.add(order)
    book.add(limit_sell(11, 50))

    book.levels[Decimal(10)].popleft()
    book.discard_if_empty(Decimal(10))

    assert Decimal(10) not in book.levels
    assert book.best_price() == Decimal(11)
