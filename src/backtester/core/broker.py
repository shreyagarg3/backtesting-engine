from typing import Dict
from collections import defaultdict
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

        self._pending_orders: Dict[str, deque] = defaultdict(deque)

        self.event_manager.subscribe("pending_orders", self._on_order_submitted)
        self.event_manager.subscribe("market_bars", self._on_market_bar)

    def _on_order_submitted(self, order_event: OrderEvent):
        self._pending_orders[order_event.symbol].append(order_event)

    def _on_market_bar(self, market_event: MarketEvent):
        bar = market_event.bar
        self.portfolio.update_latest_price(market_event.symbol, bar.close)

        orders = self._pending_orders[market_event.symbol]
        while orders:
            order = orders.popleft()
            slippage_factor = self.slippage if order.direction == Direction.BUY else -self.slippage

            fill_price = bar.close * (1.0 + slippage_factor)
            commission = self.commission_per_share * order.quantity
            
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

        self.portfolio.update_valuation(market_event.bar.timestamp)

    @property
    def cash(self) -> float:
        return self.portfolio.cash

    @property
    def portfolio_value(self) -> float:
        return self.portfolio.total_valuation