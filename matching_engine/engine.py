from matching_engine.books.lob import LimitOrderBook
from matching_engine.orders.order import Order
from decimal import Decimal, InvalidOperation

class MatchingEngine:
    def __init__(self) -> None:
        self.lob = LimitOrderBook()

    @staticmethod
    def _parse_decimal(token: str) -> Decimal | None:
        try:
            value = Decimal(token)
        except InvalidOperation:
            return None
        if not value.is_finite():
            return None
        if value <= 0:
            return None
        return value

    def _parse_order(self, order: str) -> dict | None:
        order_list = order.lower().split()

        if len(order_list) not in (3, 4, 5):
            return None
        if order_list[0] not in ("limit", "market", "update", "cancel"):
            return None

        order_type, side = order_list[0], order_list[1]
        order_id = None
        price = None
        qty = None
        if order_type == "limit":
            if len(order_list) != 4 or side not in ("buy", "sell"):
                return None
            price = self._parse_decimal(order_list[2])
            qty = self._parse_decimal(order_list[3])
            if price is None or qty is None:
                return None

        elif order_type == "market":
            if len(order_list) != 3 or side not in ("buy", "sell"):
                return None
            qty = self._parse_decimal(order_list[2])
            if qty is None:
                return None

        elif order_type == "cancel":
            if len(order_list) != 3 or side != "order":
                return None
            order_id = order_list[2]

        elif order_type == "update":
            if len(order_list) != 5 or side != "order":
                return None
            price = self._parse_decimal(order_list[2])
            qty = self._parse_decimal(order_list[3])
            if price is None or qty is None:
                return None
            order_id = order_list[4]

        return {
            "tipo": order_type,
            "side": side,
            "price": price,
            "qty": qty,
            "order_id": order_id
        }

    def run(self):
        print(">>> Match engine aberta!\n")
        while True:
            raw_order = input(">>> Digite sua ordem: ")
            if raw_order == "quit":
                print(">>> Match engine fechada!")
                break
            elif raw_order == "print book":
                self.lob.render()
                continue

            order_dict = self._parse_order(order=raw_order)
            if order_dict is None:
                print(">>> Ordem inválida")
                continue

            if order_dict["tipo"] == "cancel":
                self.lob.cancel_order(order_id=order_dict["order_id"])
                continue

            if order_dict["tipo"] == "update":
                self.lob.update_order(order_id=order_dict["order_id"], new_price=order_dict["price"], new_quant=order_dict["qty"])
                continue

            order = Order(side=order_dict["side"], type=order_dict["tipo"], quantity=order_dict["qty"], price=order_dict["price"])
            trades = self.lob.submit(order=order)
            for trade in self.lob.aggregate(trades):
                print(trade)