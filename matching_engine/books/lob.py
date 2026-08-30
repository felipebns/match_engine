from matching_engine.books.book import Book

class LimitOrderBook():
    def __init__(self):
        self.bid_side = Book()
        self.ask_side = Book()