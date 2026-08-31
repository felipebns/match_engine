from decimal import Decimal
import itertools

ID_COUNTER = itertools.count(1)

class Order:
    def __init__(self, side: str, type: str, quantity: Decimal, price: Decimal | None = None) -> None:
        self.side = side
        self.type = type
        self.quantity = quantity
        self.price = price

        self.order_id = self._next_order_id()
        self.filled_quantity = Decimal(0)
        self.status = "NEW"

    @property
    def remaining_quantity(self) -> Decimal:
        """Quantidade ainda em aberto."""
        return self.quantity - self.filled_quantity

    @property
    def is_active(self) -> bool:
        """True enquanto a ordem ainda pode gerar trades."""
        return self.status not in ("FILLED", "CANCELLED")

    @property
    def opposite_side(self) -> str:
        """Lado contrario -- usado para achar o livro contra o qual cruzar."""
        return "sell" if self.side == "buy" else "buy"

    def _next_order_id(self) -> str:
        return f"order-{next(ID_COUNTER)}"

    def fill(self, quantity: Decimal) -> None:
        self.filled_quantity += quantity
        self.status = "FILLED" if self.remaining_quantity == 0 else "PARTIALLY_FILLED"

    def cancel(self) -> None:
        self.status = "CANCELLED"
