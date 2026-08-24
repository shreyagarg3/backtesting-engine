from collections import defaultdict
from ..data.events import FillEvent

class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.total_valuation = initial_capital
        self.cash = initial_capital
        self._latest_prices = defaultdict(float)

    def update_on_fill(self, fill: FillEvent):
        self._latest_prices[fill.symbol] = fill.fill_cost
        # To do - update state of the portfolio when an order is filled