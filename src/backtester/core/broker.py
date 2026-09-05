from collections import deque
from ..data.events import OrderEvent, FillEvent, MarketEvent, Direction
from ..utils.event_manager import EventManager
from ..utils.logger import get_logger
from ..core.portfolio import Portfolio

logger = get_logger(__name__)


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
        bar = market_event.bar
        symbol = market_event.symbol

        unprocessed_orders = deque()
        while len(self._pending_orders) > 0:
            order: OrderEvent = self._pending_orders.popleft()

            # Only execute orders for the current bar's symbol
            if order.symbol != symbol:
                unprocessed_orders.append(order)
                continue

            slippage_factor = self.slippage if order.direction == Direction.BUY else -self.slippage
            fill_price = bar.close * (1.0 + slippage_factor)

            # Calculate Commission (£1.00 min)
            commission = max(1.00, self.commission_per_share * order.quantity)

            fill = FillEvent(
                time_index=bar.timestamp,
                symbol=order.symbol,
                quantity=order.quantity,
                direction=order.direction,
                fill_price=fill_price,
                commission=commission,
            )

            logger.info(
                f"ORDER FILLED: {fill.direction} {fill.quantity} {fill.symbol} "
                f"@ £{fill.fill_price:.2f} (Slippage: {slippage_factor:+.4%}, Commission: £{commission:.2f})"
            )

            self.portfolio.update_on_fill(fill)
            self.event_manager.publish("order_fills", fill)

        self._pending_orders = unprocessed_orders

    @property
    def cash(self) -> float:
        return self.portfolio.cash

    @property
    def portfolio_value(self) -> float:
        return self.portfolio.total_valuation