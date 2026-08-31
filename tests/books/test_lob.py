"""Testes do LimitOrderBook: cruzamento de ordens."""

from decimal import Decimal

from matching_engine.books.lob import LimitOrderBook


def test_ordem_sem_contraparte_repousa_no_livro(limit_buy):
    lob = LimitOrderBook()
    trades = lob.submit(limit_buy(10, 100))

    assert trades == []
    assert lob.best_bid == Decimal(10)


def test_market_sem_liquidez_nao_repousa(market_buy):
    """Uma market nao tem preco, entao nao ha nivel onde esperar."""
    lob = LimitOrderBook()
    trades = lob.submit(market_buy(100))

    assert trades == []
    assert lob.ask_side.is_empty and lob.bid_side.is_empty


def test_preco_do_trade_e_o_da_ordem_passiva(limit_sell, limit_buy):
    """Quem esperava no livro tem o preco garantido."""
    lob = LimitOrderBook()
    lob.submit(limit_sell(10, 100))
    trades = lob.submit(limit_buy(15, 100))

    assert len(trades) == 1
    assert trades[0].price == Decimal(10)


def test_limit_agressiva_executa_e_repousa_o_saldo(limit_sell, limit_buy):
    lob = LimitOrderBook()
    lob.submit(limit_sell(10, 60))
    trades = lob.submit(limit_buy(10, 100))

    assert trades[0].quantity == Decimal(60)
    assert lob.best_bid == Decimal(10)
    assert lob.bid_side.levels[Decimal(10)].total_quantity == Decimal(40)


def test_market_percorre_varios_niveis(limit_sell, market_buy):
    lob = LimitOrderBook()
    lob.submit(limit_sell(10, 50))
    lob.submit(limit_sell(11, 50))
    trades = lob.submit(market_buy(100))

    assert [t.price for t in trades] == [Decimal(10), Decimal(11)]


def test_limit_respeita_o_proprio_limite(limit_sell, limit_buy):
    """Compra a 10 nao paga 11."""
    lob = LimitOrderBook()
    lob.submit(limit_sell(11, 100))
    trades = lob.submit(limit_buy(10, 100))

    assert trades == []
    assert lob.best_bid == Decimal(10)
    assert lob.best_offer == Decimal(11)


def test_livro_nunca_fica_cruzado(limit_sell, limit_buy):
    """Invariante: best_bid < best_offer sempre."""
    lob = LimitOrderBook()
    lob.submit(limit_sell(10, 50))
    lob.submit(limit_buy(12, 100))

    assert lob.best_offer is None or lob.best_bid < lob.best_offer


def test_fifo_no_mesmo_preco(limit_sell, market_buy):
    """Requisito adicional 2, ponta a ponta."""
    lob = LimitOrderBook()
    primeira, segunda = limit_sell(20, 100), limit_sell(20, 200)
    lob.submit(primeira)
    lob.submit(segunda)
    lob.submit(market_buy(150))

    assert primeira.status == "FILLED"
    assert segunda.remaining_quantity == Decimal(150)
