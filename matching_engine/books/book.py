from matching_engine.books.price_level import PriceLevel
from matching_engine.orders.order import Order
from decimal import Decimal

class Book:
    def __init__(self, side: str) -> None:
        self.side = side
        self.levels: dict[Decimal, PriceLevel] = {} # levels é a fila que existe para valor no book
        self.ids_to_orders: dict[str, Order] = {} # reverso para poder achar a qual fila pertence a ordem sem ter que percorrer tudo

    @property
    def is_empty(self) -> bool:
        return len(self.levels) == 0

    def add(self, order: Order) -> None:
        """Insere a ordem no nivel do seu preco, criando o nivel se preciso."""
        if order.price not in self.levels:
            self.levels[order.price] = PriceLevel()
        self.levels[order.price].add(order)
        self.ids_to_orders[order.order_id] = order

    def remove(self, order_id: str) -> None:
        """Retira a ordem e descarta o nivel se ele ficar vazio."""
        try:
            order = self.ids_to_orders[order_id]
            self.levels[order.price].remove(order)
            self.discard_if_empty(order.price)
            del self.ids_to_orders[order_id]
            print("Order cancelled")
        except KeyError:
            print(f"Não há ordem com ID: {order_id} em Book {self.side}")

    def discard_if_empty(self, price: Decimal) -> None:
        if self.levels[price].is_empty:
            del self.levels[price]

    def sorted_prices(self) -> list[Decimal]:
        """Precos do mais agressivo para o menos agressivo."""
        return sorted(self.levels, reverse=(self.side == "buy"))

    def best_price(self) -> Decimal | None:
        """Melhor preco deste lado. None se o lado estiver vazio."""
        prices = self.sorted_prices()
        return prices[0] if prices else None
