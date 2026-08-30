from decimal import Decimal

class Trade:
    def __init__(self, price: Decimal, quantity: Decimal, aggressor_order_id: str, resting_order_id: str) -> None:
        self.price = price
        self.quantity = quantity
        self.aggressor_order_id = aggressor_order_id
        self.resting_order_id = resting_order_id
