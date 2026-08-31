from matching_engine.books.price_level import PriceLevel
from matching_engine.orders.order import Order
from decimal import Decimal

class Book:
    def __init__(self, side: str) -> None:
        self.side = side
        self.levels: dict[Decimal, PriceLevel] = {}

    @property
    def is_empty(self) -> bool:
        return len(self.levels) == 0

    def add(self, order: Order) -> None:
        """Insere a ordem no nivel do seu preco, criando o nivel se preciso."""
        if order.price not in self.levels:
            self.levels[order.price] = PriceLevel(order.price)
        self.levels[order.price].add(order)

    def remove(self, order: Order) -> None:
        """Retira a ordem e descarta o nivel se ele ficar vazio."""
        level = self.levels[order.price]
        level.remove(order)
        if level.is_empty:
            del self.levels[order.price]

    def sorted_prices(self) -> list[Decimal]:
        """Precos do mais agressivo para o menos agressivo."""
        return sorted(self.levels, reverse=(self.side == "buy"))

    def best_price(self) -> Decimal | None:
        """Melhor preco deste lado. None se o lado estiver vazio."""
        prices = self.sorted_prices()
        return prices[0] if prices else None

    def best_level(self) -> PriceLevel | None:
        """Nivel do melhor preco. None se o lado estiver vazio."""
        price = self.best_price()
        return self.levels[price] if price is not None else None

    def __repr__(self) -> str:
        return f"<Book {self.side} levels={self.sorted_prices()}>"