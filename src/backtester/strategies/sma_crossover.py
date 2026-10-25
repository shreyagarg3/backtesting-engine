from typing import Optional
import numpy as np
from ..data.events import Bar, SignalType, SignalEvent
from ..indicators.moving_average import compute_sma
from ..utils.event_manager import EventManager
from .strategy import Strategy


class SMACrossover(Strategy):
    def __init__(self, event_manager: EventManager, fast_window: int, slow_window: int):
        super().__init__(event_manager, window_size=slow_window + 1)
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signal(self, symbol: str, bar: Bar) -> Optional[SignalEvent]:
        history = self.symbol_data[symbol]
        
        # Ensure we have enough bars to compute the slow SMA
        if len(history) < self.slow_window + 1:
            return

        closes = [b.close for b in history]

        # Calculate current (T) and previous (T-1) SMAs
        curr_fast_sma = compute_sma(closes, self.fast_window)
        curr_slow_sma = compute_sma(closes, self.slow_window)

        prev_fast_sma = compute_sma(closes[:-1], self.fast_window)
        prev_slow_sma = compute_sma(closes[:-1], self.slow_window)

        if prev_fast_sma <= prev_slow_sma and curr_fast_sma > curr_slow_sma:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.LONG, strength=1.0)
        elif prev_fast_sma >= prev_slow_sma and curr_fast_sma < curr_slow_sma:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.EXIT, strength=1.0)