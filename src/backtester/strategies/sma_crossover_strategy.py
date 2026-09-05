import numpy as np
from ..data.events import Bar, SignalType
from ..utils.event_manager import EventManager
from ..utils.logger import get_logger
from ..strategies.base_strategy import BaseStrategy

logger = get_logger(__name__)


class SMACrossoverStrategy(BaseStrategy):
    def __init__(self, event_manager: EventManager, fast_window: int, slow_window: int):
        super().__init__(event_manager, window_size=slow_window + 1)
        self.fast_window = fast_window
        self.slow_window = slow_window

    def calculate_signals(self, symbol: str, bar: Bar):
        history = self.symbol_data[symbol]
        
        # Ensure we have enough bars to compute the slow SMA
        if len(history) < self.slow_window + 1:
            return

        closes = [b.close for b in history]

        # Calculate current (T) and previous (T-1) SMAs
        fast_sma_curr = np.mean(closes[-self.fast_window:])
        slow_sma_curr = np.mean(closes[-self.slow_window:])
        
        fast_sma_prev = np.mean(closes[-self.fast_window - 1:-1])
        slow_sma_prev = np.mean(closes[-self.slow_window - 1:-1])

        if fast_sma_prev <= slow_sma_prev and fast_sma_curr > slow_sma_curr:
            self._emit_signal(symbol, bar.timestamp, SignalType.LONG, strength=1.0)
            logger.info(
                f"[{symbol}] BULLISH CROSSOVER detected at {bar.timestamp} | "
                f"Fast SMA ({self.fast_window}): {fast_sma_prev:.2f} -> {fast_sma_curr:.2f} | "
                f"Slow SMA ({self.slow_window}): {slow_sma_prev:.2f} -> {slow_sma_curr:.2f}"
            )
        elif fast_sma_prev >= slow_sma_prev and fast_sma_curr < slow_sma_curr:
            self._emit_signal(symbol, bar.timestamp, SignalType.EXIT, strength=1.0)
            logger.info(
                f"[{symbol}] BEARISH CROSSOVER detected at {bar.timestamp} | "
                f"Fast SMA ({self.fast_window}): {fast_sma_prev:.2f} -> {fast_sma_curr:.2f} | "
                f"Slow SMA ({self.slow_window}): {slow_sma_prev:.2f} -> {slow_sma_curr:.2f}"
            )