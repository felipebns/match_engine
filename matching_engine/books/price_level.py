class PriceLevel:
    def __init__(self, price):
        self.price = price
        self.orders = deque()      # [primeira a chegar, ..., última]

    def add(self, order):
        self.orders.append(order)  # entra no FIM

    def peek(self):
        return self.orders[0]      # a PRÓXIMA a executar

    def popleft(self):
        return self.orders.popleft()

    def remove(self, order):
        self.orders.remove(order)  # cancelamento
