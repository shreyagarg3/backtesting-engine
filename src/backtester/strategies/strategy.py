from abc import ABC, abstractmethod
from typing import Dict, Optional
from collections import defaultdict, deque
from ..data.events import SignalEvent, MarketEvent, Bar
from ..utils.event_manager import EventManager


class Strategy(ABC):
    def __init__(self, event_manager: EventManager, window_size: int):
        self.event_manager = event_manager
        self.symbol_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.event_manager.subscribe("market_bars", self._on_market_bar)

    def _on_market_bar(self, market_event: MarketEvent):
        self.symbol_data[market_event.symbol].append(market_event.bar)
        signal = self.generate_signal(market_event.symbol, market_event.bar)
        
        if signal is not None:
            self.event_manager.publish("signals", signal)

    @abstractmethod
    def generate_signal(self, symbol: str, bar: Bar) -> Optional[SignalEvent]:
        pass