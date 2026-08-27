from data.events import SignalEvent, OrderEvent, OrderType, Direction
from backtester.utils.event_manager import EventManager
from backtester.core.portfolio import Portfolio


class ExecutionHandler:
    def __init__(self, event_manager: EventManager, portfolio: Portfolio):
        self.event_manager = event_manager
        self.portfolio = portfolio

        self.event_manager.subscribe("signals", self.on_signal)

    def on_signal(self, signal: SignalEvent):
        order = OrderEvent(
            symbol=signal.symbol,
            order_type=OrderType.MARKET,
            quantity=1,
            direction=Direction.BUY
        )

        self.event_manager.publish("pending_orders", order)