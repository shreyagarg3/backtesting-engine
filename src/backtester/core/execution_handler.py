from typing import Dict
from collections import defaultdict
from ..data.events import SignalEvent, OrderEvent, MarketEvent, Direction, SignalType
from ..utils.event_manager import EventManager
from ..utils.logger import get_logger
from ..core.portfolio import Portfolio

logger = get_logger(__name__)


class ExecutionHandler:
    def __init__(self, event_manager: EventManager, portfolio: Portfolio, max_position_perc: float = 0.10):
        self.event_manager = event_manager
        self.portfolio = portfolio
        self.max_position_perc = max_position_perc
        self._latest_prices: Dict[str, float] = defaultdict()

        self.event_manager.subscribe("market_bars", self.on_market_bar)
        self.event_manager.subscribe("signals", self.on_signal)

    def on_market_bar(self, market_event: MarketEvent):
        self._latest_prices[market_event.symbol] = market_event.bar.close

    def on_signal(self, signal: SignalEvent):
        price = self._latest_prices.get(signal.symbol)
        if price <= 0:
            logger.warning(f"[{signal.symbol}] SIGNAL REJECTED: Missing or invalid market price ({price}).")
            return
        
        current_qty = self.portfolio.get_position(signal.symbol)

        if signal.signal_type == SignalType.EXIT:
            if current_qty == 0:
                logger.debug(f"[{signal.symbol}] EXIT SIGNAL IGNORED: No open position to exit.")
                return

            logger.info(
                f"[{signal.symbol}] EXIT SIGNAL TRIGGERED: Submitting {direction.name} order "
                f"for {abs(current_qty)} shares to close open position."
            )
            
            direction = Direction.SELL if current_qty > 0 else Direction.BUY
            order = OrderEvent(symbol=signal.symbol, direction=direction, quantity=abs(current_qty))
            self.event_manager.publish("pending_orders", order)
            return

        # Determine position size based on equity % and signal strength
        target_allocation = self.portfolio.total_valuation * self.max_position_perc * signal.strength
        quantity = int(target_allocation // price)

        if quantity <= 0:
            return

        direction = Direction.BUY if signal.signal_type == SignalType.LONG else Direction.SELL
        if direction == Direction.BUY:
            max_affordable = int(self.portfolio.cash // price)
            quantity = min(quantity, max_affordable)

            if quantity <= 0:
                logger.warning(f"[{signal.symbol}] BUY REJECTED: Insufficient cash (£{self.portfolio.cash:.2f}) for share price (£{price:.2f}).")
                return

        logger.info(
            f"[{signal.symbol}] ORDER SUBMITTED: {direction.name} {quantity} shares @ est. £{price:.2f} | "
            f"Target Value: £{(quantity * price):.2f} (Portfolio Equity: £{self.portfolio.total_valuation:.2f})"
        )

        order = OrderEvent(symbol=signal.symbol, direction=direction, quantity=quantity)
        self.event_manager.publish("pending_orders", order)