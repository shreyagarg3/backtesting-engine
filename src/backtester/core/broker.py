from collections import deque
from ..data.events import OrderEvent, FillEvent, MarketEvent, Direction
from ..utils.event_manager import EventManager
from ..core.portfolio import Portfolio

class Broker:
    def __init__(self, event_manager: EventManager, initial_capital: float, commission_per_share: float, slippage: float):
        self.event_manager = event_manager
        self.portfolio = Portfolio(initial_capital=initial_capital)
        self.commission_per_share = commission_per_share
        self.slippage = slippage

        self._pending_orders = deque()

        self.event_manager.subscribe("pending_orders", self.on_order_submitted)
        self.event_manager.subscribe("market_bars", self.on_market_bar)

    def on_order_submitted(self, order_event: OrderEvent):
        self._pending_orders.append(order_event)

    def on_market_bar(self, market_event: MarketEvent):
        closing_price = market_event["bar"].close

        while len(self._pending_orders) > 0:
            order: OrderEvent = self._pending_orders.popleft()
            fill_price = closing_price * (1.0 + (self.slippage if Direction.BUY else -self.slippage))

            # Minimum of £1 commission per share
            commission = max(1.00, self.commission_per_share * order.quantity)

            fill = FillEvent(
                time_index=market_event["bar"].timestamp,
                symbol=order.symbol,
                quantity=order.quantity,
                direction=order.direction,
                fill_price=fill_price,
                commission=commission,
            )

            self.portfolio.update_on_fill(fill)
            self.event_manager.publish("order_fills", fill)

    @property
    def cash(self) -> float:
        return self.portfolio.cash

    @property
    def portfolio_value(self) -> float:
        return self.portfolio.total_valuation