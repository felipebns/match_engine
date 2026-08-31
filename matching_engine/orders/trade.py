from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Trade: 
    price: Decimal
    quantity: Decimal
    aggressor_order_id: str
    resting_order_id: str

    def __str__(self) -> str:
        """trade formatado para printar na tela."""
        return f"Trade, price: {self.price}, qty: {self.quantity}"
