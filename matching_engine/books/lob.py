from matching_engine.orders.order import Order
from matching_engine.orders.trade import Trade
from matching_engine.books.book import Book

class LimitOrderBook():
    def __init__(self):
        self.bid_side = Book()
        self.ask_side = Book()
        self.trades = []

    def _match(self, order: Order) -> None:
        return 1

    def submit(self, order: Order) -> list[Trade]:
        trades = self._match(order) 
        if order.type == "limit" and order.remaining_quantity > 0:
            if order.side == "buy":
                self.bid_side.add_to_queue(order)
            elif order.side == "sell":
                self.ask_side.add_to_queue(order)
        self.trades.extend(trades)
        return trades