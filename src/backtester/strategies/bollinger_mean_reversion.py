from typing import Optional
from ..data.events import Bar, SignalType, SignalEvent
from ..utils.event_manager import EventManager
from ..utils.logger import get_logger
from .strategy import Strategy
from ..indicators.bollinger_bands import compute_bollinger_bands

logger = get_logger(__name__)


class BollingerMeanReversion(Strategy):
    def __init__(self, event_manager: EventManager, window: int, num_std: float):
        super().__init__(event_manager, window_size=window + 1)
        self.window = window
        self.num_std = num_std

    def generate_signal(self, symbol: str, bar: Bar) -> Optional[SignalEvent]:
        history = self.symbol_data[symbol]

        # Ensure we have enough bars to compute the bands
        if len(history) < self.window + 1:
            return

        closes = [b.close for b in history]

        middle_prev, upper_prev, lower_prev = compute_bollinger_bands(closes[:-1], self.window, self.num_std)
        _, upper_curr, lower_curr = compute_bollinger_bands(closes, self.window, self.num_std)

        prev_price = closes[-2]
        curr_price = closes[-1]

        # LONG: Price dips below the lower band and bounces back inside
        if prev_price <= lower_prev and curr_price > lower_curr:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.LONG, strength=1.0)

        # EXIT: Price reaches the overbought upper band
        elif prev_price < upper_prev and curr_price >= upper_curr:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.EXIT, strength=1.0)

        # EXIT: Price reverts back up to cross the middle SMA
        elif prev_price <= middle_prev and curr_price > middle_prev:
            return SignalEvent(symbol=symbol, timestamp=bar.timestamp, signal_type=SignalType.EXIT, strength=1.0)

        return None