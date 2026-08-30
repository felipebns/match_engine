from decimal import Decimal
import itertools

ID_COUNTER = itertools.count(1)

class Order:
    def __init__(self, side: str, order_type: str, quantity: Decimal, price: Decimal | None = None) -> None:
        self.side = side
        self.order_type = order_type
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
        return self.status not in (OrderStatus.FILLED, OrderStatus.CANCELLED)

    def _next_order_id(self) -> str:
        return f"order-{next(ID_COUNTER)}"

    def fill(self, quantity: Decimal) -> None:
        """Aplica uma execucao, parcial ou total."""
        if quantity <= 0:
            raise ValueError("quantidade executada deve ser positiva")
        if quantity > self.remaining_quantity:
            raise ValueError("execucao maior que a quantidade em aberto")

        self.filled_quantity += quantity
        self.status = (
            OrderStatus.FILLED
            if self.remaining_quantity == 0
            else OrderStatus.PARTIALLY_FILLED
        )

    def cancel(self) -> None:
        """Cancela a ordem. Uma ordem ja executada nao pode ser cancelada."""
        if self.status is OrderStatus.FILLED:
            raise ValueError("ordem ja executada nao pode ser cancelada")
        self.status = OrderStatus.CANCELLED