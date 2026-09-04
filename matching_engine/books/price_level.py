from matching_engine.orders.order import Order
from collections import deque
from decimal import Decimal

class PriceLevel:
    def __init__(self) -> None:
        #retirei o atributo price pq ele não fazia nada
        self.orders: deque[Order] = deque() # deque é muito mais rápido para a operação pop, muito frequente

    @property
    def total_quantity(self) -> Decimal:
        """Soma da quantidade em aberto de todas as ordens do nivel."""
        return sum((o.remaining_quantity for o in self.orders), Decimal(0))

    @property
    def is_empty(self) -> bool:
        return len(self.orders) == 0

    def add(self, order: Order) -> None:
        """Coloca a ordem no FIM da fila."""
        self.orders.append(order)

    def peek(self) -> Order:
        """Proxima ordem a executar, sem retirar da fila."""
        return self.orders[0]

    def popleft(self) -> Order:
        """Retira e devolve a proxima ordem a executar."""
        return self.orders.popleft()

    def remove(self, order: Order) -> None:
        """Retira uma ordem especifica da fila."""
        self.orders.remove(order)
