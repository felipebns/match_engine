from decimal import Decimal, InvalidOperation
from matching_engine.orders.order import Order

class MatchingEngine:
    @staticmethod
    def _parse_decimal(token: str) -> Decimal | None:
        try:
            value = Decimal(token)
        except InvalidOperation:
            return None
        if value <= 0:
            return None
        return value

    def _parse_order(self, order: str) -> dict | None:
        order_list = order.lower().split()

        if len(order_list) not in (3, 4):
            return None
        if order_list[0] not in ("limit", "market"):
            return None
        if order_list[1] not in ("buy", "sell"):
            return None

        order_type, side = order_list[0], order_list[1]
        if order_type == "limit":
            if len(order_list) != 4:
                return None
            price = self._parse_decimal(order_list[2])
            qty = self._parse_decimal(order_list[3])
            if price is None or qty is None:
                return None

        elif order_type == "market":
            if len(order_list) != 3:
                return None
            price = None
            qty = self._parse_decimal(order_list[2])
            if qty is None:
                return None

        return {
            "tipo": order_type,
            "side": side,
            "price": price,
            "qty": qty,
        }

    def run(self):
        print(">>> Match engine aberta!\n")
        while True:
            raw_order = input(">>> Digite sua ordem: ")
            if raw_order.strip().lower() == "quit":
                print(">>> Match engine fechada!")
                break

            order_dict = self._parse_order(order=raw_order)
            if order_dict is None:
                print(">>> Ordem inválida")
                continue

            order = Order(side=order_dict["side"], order_type=order_dict["tipo"], quantity=order_dict["tqy"], price=order_dict["price"])