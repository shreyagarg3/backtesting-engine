from typing import Optional
from ..data.events import Bar, SignalType, SignalEvent
from ..utils.event_manager import EventManager
from ..strategies.strategy import Strategy
from ..indicators.stochastic import compute_stochastic


class StochasticCrossover(Strategy):
    def __init__(self, event_manager: EventManager, k_window: int, d_window: int):
        super().__init__(event_manager, window_size=k_window + d_window + 1)
        self.k_window = k_window
        self.d_window = d_window

    def generate_signal(self, symbol: str, bar: Bar) -> Optional[SignalEvent]:
        history = self.symbol_data[symbol]
        if len(history) < self.k_window + self.d_window + 1:
            return

        highs = [b.high for b in history]
        lows = [b.low for b in history]
        closes = [b.close for b in history]

        # Calculate current (T) and previous (T-1) %K and %D values
        curr_k, curr_d = compute_stochastic(highs, lows, closes, self.k_window, self.d_window)
        prev_k, prev_d = compute_stochastic(highs[:-1], lows[:-1], closes[:-1], self.k_window, self.d_window)

        # LONG: %K crosses above %D
        if prev_k <= prev_d and curr_k > curr_d:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.LONG, strength=1.0)

        # EXIT: %K crosses below %D
        elif prev_k >= prev_d and curr_k < curr_d:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.EXIT, strength=1.0)

        return None