from dataclasses import dataclass
from decimal import Decimal

"""Classe que representa uma operação de negociação."""
@dataclass(frozen=True) # Objeto imutável
class Trade: 
    price: Decimal
    quantity: Decimal
    aggressor_order_id: str
    resting_order_id: str

    def __str__(self) -> str:
        """trade formatado para printar na tela."""
        return f"Trade, price: {self.price}, qty: {self.quantity}"
