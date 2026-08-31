from matching_engine.orders.order import Order
from matching_engine.orders.trade import Trade
from matching_engine.books.book import Book
from decimal import Decimal

class LimitOrderBook:
    def __init__(self) -> None:
        self.bid_side = Book("buy")
        self.ask_side = Book("sell")
        self.trades: list[Trade] = []

    def side_book(self, side: str) -> Book:
        """Devolve o Book do lado pedido."""
        return self.bid_side if side == "buy" else self.ask_side

    @property
    def best_bid(self) -> Decimal | None:
        return self.bid_side.best_price()

    @property
    def best_offer(self) -> Decimal | None:
        return self.ask_side.best_price()

    @staticmethod
    def _crosses(order: Order, price: Decimal) -> bool:
        if order.type == "market":
            return True
        if order.side == "buy":
            return price <= order.price
        return price >= order.price

    @staticmethod
    def _execute(aggressor: Order, resting: Order) -> Trade:
        quantity = min(aggressor.remaining_quantity, resting.remaining_quantity)
        aggressor.fill(quantity)
        resting.fill(quantity)
        return Trade(
            price=resting.price,
            quantity=quantity,
            aggressor_order_id=aggressor.order_id,
            resting_order_id=resting.order_id,
        )

    def _match(self, order: Order) -> list[Trade]:
        trades: list[Trade] = []
        opposite = self.side_book(order.opposite_side)

        for price in opposite.sorted_prices():
            if order.remaining_quantity == 0:
                break
            if not self._crosses(order, price):
                break

            level = opposite.levels[price]
            while not level.is_empty and order.remaining_quantity > 0:
                resting = level.peek()
                trades.append(self._execute(order, resting))
                if resting.remaining_quantity == 0:
                    level.popleft()

            opposite.discard_if_empty(price)

        return trades

    def submit(self, order: Order) -> list[Trade]:
        trades = self._match(order)
        if order.type == "limit" and order.remaining_quantity > 0:
            self.side_book(order.side).add(order)
        self.trades.extend(trades)
        return trades

    @staticmethod
    def aggregate(trades: list[Trade]) -> list[Trade]:
        agregados: list[Trade] = []
        for trade in trades:
            if agregados and agregados[-1].price == trade.price:
                anterior = agregados[-1]
                agregados[-1] = Trade(
                    price=anterior.price,
                    quantity=anterior.quantity + trade.quantity,
                    aggressor_order_id=anterior.aggressor_order_id,
                    resting_order_id=anterior.resting_order_id,
                )
            else:
                agregados.append(trade)
        return agregados

    def render(self) -> str:
        """Livro em duas colunas, para visualizacao."""
        bids = [(p, self.bid_side.levels[p].total_quantity) for p in self.bid_side.sorted_prices()]
        asks = [(p, self.ask_side.levels[p].total_quantity) for p in self.ask_side.sorted_prices()]

        lines = ["Ordens de Compra    | Ordens de Venda", "--------------------|-----------------"]
        for i in range(max(len(bids), len(asks))):
            left = f"{bids[i][1]} @ {bids[i][0]}" if i < len(bids) else ""
            right = f"{asks[i][1]} @ {asks[i][0]}" if i < len(asks) else ""
            lines.append(f"{left:<20}| {right}")
        return "\n".join(lines)