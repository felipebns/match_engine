from matching_engine.orders import Order

class MatchingEngine:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _clean_order(order: str) -> list[str]:
        return order.lower().split()

    def run(self):
        print(">>> Match engine aberta!\n")
        while True:
            raw_order = input(">>> Digite sua ordem: ")
            self.order = Order(raw_order=raw_order)
            order_tokens = self._clean_order(order=raw_order)
            self.order.set_order_tokens(order_tokens=order_tokens)

            if len(order_tokens) < 1:
                continue
            if order_tokens[0] == "quit":
                print(">>> Match engine fechada!")
                break

            self.order.execute()
            print()