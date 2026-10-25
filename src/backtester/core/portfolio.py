from collections import defaultdict
from ..data.events import FillEvent, Direction


class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.total_valuation = initial_capital
        self.cash = initial_capital

        self._latest_prices = defaultdict(float)
        self._positions = defaultdict(int)
        self.equity_curve = []

    def update_on_fill(self, fill_event: FillEvent):
        trade_cost = fill_event.fill_price * fill_event.quantity
        direction_mult = 1 if fill_event.direction == Direction.BUY else -1

        # Update share position and latest fill price
        self._positions[fill_event.symbol] += fill_event.quantity * direction_mult
        self._latest_prices[fill_event.symbol] = fill_event.fill_price

        self.cash -= (trade_cost * direction_mult) + fill_event.commission

    def update_latest_price(self, symbol: str, price: float):
        self._latest_prices[symbol] = price

    def get_position(self, symbol: str) -> int:
        return self._positions[symbol]

    def update_valuation(self, timestamp: str):
        holdings_market_value = sum(
            quantity * self._latest_prices[symbol]
            for symbol, quantity in self._positions.items()
        )

        self.total_valuation = self.cash + holdings_market_value
        self.equity_curve.append(self.total_valuation)