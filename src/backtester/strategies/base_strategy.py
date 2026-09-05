from abc import ABC, abstractmethod
from typing import Dict, Any
from collections import defaultdict, deque
from ..data.events import SignalEvent, MarketEvent, Bar
from ..utils.event_manager import EventManager


class BaseStrategy(ABC):
    def __init__(self, event_manager: EventManager, window_size: int):
        self.event_manager = event_manager
        self.symbol_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))

        self.event_manager.subscribe("market_bars", self.on_market_bar)

    def on_market_bar(self, market_event: MarketEvent):
        self.symbol_data[market_event.symbol].append(market_event.bar)
        self.calculate_signals(market_event.symbol, market_event.bar)

    @abstractmethod
    def calculate_signals(self, symbol: str, bar: Bar):
        pass

    def _emit_signal(self, symbol: str, timestamp: Any, signal_type: str, strength: float):
        signal = SignalEvent(
            symbol=symbol,
            timestamp=timestamp,
            signal_type=signal_type,
            strength=strength
        )

        self.event_manager.publish("signals", signal)