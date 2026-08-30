class Order:
    def __init__(self, raw_order: str):
        self.raw_order = raw_order
        self.order_tokens = None

    def set_order_tokens(self, order_tokens: list[str]) -> None:
        self.order_tokens = order_tokens

    @staticmethod
    def execute() -> None:
        pass