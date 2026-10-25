from datetime import datetime
from enum import Enum
from ..data.bar import Bar


class SignalType(Enum):
    LONG = 1
    SHORT = 2
    EXIT = 3

class OrderType(Enum):
    MARKET = 1
    LIMIT = 2

class Direction(Enum):
    BUY = 1
    SELL = 2

    def __str__(self):
        return self.name

class EventType(Enum):
    MARKET = 1
    SIGNAL = 2
    ORDER = 3
    FILL = 4

class Event:
    pass

class MarketEvent(Event):
    def __init__(self, symbol: str, bar: Bar):
        self.symbol = symbol
        self.bar = bar

class SignalEvent(Event):
    def __init__(self, symbol: str, timestamp: datetime, signal_type: SignalType, strength: float = 1.0):
        self.symbol = symbol
        self.timestamp = timestamp
        self.signal_type = signal_type
        self.strength = strength

class OrderEvent(Event):
    def __init__(self, symbol: str, quantity: int, direction: Direction):
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction

class FillEvent(Event):
    def __init__(self, time_index: datetime, symbol: str, quantity: int, direction: Direction, fill_price: float, commission: float = 0.0):
        self.time_index = time_index
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        self.commission = commission