from matching_engine.books.price_level import PriceLevel
from matching_engine.orders.order import Order

class Book:
    def __init__(self):
        self.queue = []

    def add_to_queue(self, order: Order):
        pass