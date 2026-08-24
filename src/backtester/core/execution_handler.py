from collections import deque
from backtester.data.events import OrderEvent, MarketEvent, FillEvent, Direction
from backtester.utils.event_manager import EventManager

class ExecutionHandler:
    def __init__(self, event_manager: EventManager, commission_per_share: float = 0.005, slippage_pct: float = 0.0005):
        self.event_manager = event_manager
        self.commission_per_share = commission_per_share
        self.slippage_pct = slippage_pct

        self._pending_orders = deque()

        self.event_manager.subscribe("pending_orders", self.on_order_submitted)
        self.event_manager.subscribe("market_bars", self.on_market_bar)
    
    def on_order_submitted(self, order_event: OrderEvent):
        self._pending_orders.append(order_event)

    def on_market_bar(self, market_event: MarketEvent):
        print(market_event)

        if not self._pending_orders:
            return

        while self._pending_orders:
            order: OrderEvent = self._pending_orders.popleft()
            base_price = market_event.bar["close"]

            if order.direction == Direction.BUY:
                fill_price = base_price * (1.0 + self.slippage_pct)
            else:
                fill_price = base_price * (1.0 - self.slippage_pct)

            commission = max(1.00, self.commission_per_share * order.quantity)

            fill = FillEvent(
                time_index=market_event.bar["datetime"],
                symbol=order.symbol,
                quantity=order.quantity,
                direction=order.direction,
                fill_cost=fill_price,
                commission=commission,
            )

            self.event_manager.publish("order_fills", fill)