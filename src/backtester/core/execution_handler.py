from typing import Dict
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
        self._latest_prices: Dict[str, float] = {}
        
        # Staging queue for signals received on the previous bar
        self._pending_signals: Dict[str, SignalEvent] = {}

        self.event_manager.subscribe("market_bars", self._on_market_bar)
        self.event_manager.subscribe("signals", self._on_signal)

    def _on_signal(self, signal: SignalEvent):
        self._pending_signals[signal.symbol] = signal
        logger.info(f"[{signal.symbol}] SIGNAL RECEIVED & STAGED: {signal.signal_type.name} at {signal.timestamp}")

    def _on_market_bar(self, market_event: MarketEvent):
        bar = market_event.bar
        symbol = market_event.symbol
        self._latest_prices[symbol] = bar.close

        if symbol in self._pending_signals:
            signal = self._pending_signals.pop(symbol)
            self._execute_signal(signal, bar.close)

    def _execute_signal(self, signal: SignalEvent, price: float):
        position_size = self.portfolio.get_position(signal.symbol)

        if signal.signal_type == SignalType.EXIT:
            if position_size == 0:
                logger.debug(f"[{signal.symbol}] EXIT SIGNAL IGNORED: No open position to exit.")
                return
            
            direction = Direction.SELL if position_size > 0 else Direction.BUY
            order = OrderEvent(symbol=signal.symbol, direction=direction, quantity=abs(position_size))

            logger.info(
                f"[{signal.symbol}] EXIT ORDER CREATED (T+1): Submitting {direction} "
                f"for {abs(position_size)} shares @ £{price:.2f}"
            )

            self.event_manager.publish("pending_orders", order)
            return

        # Sizing based on current bar's price (T+1)
        target_allocation = self.portfolio.total_valuation * self.max_position_perc * signal.strength
        quantity = int(target_allocation // price)

        if quantity == 0:
            logger.warning(f"[{signal.symbol}] ORDER CANCELLED: Calculated quantity is 0 at price £{price:.2f}")
            return

        direction = Direction.BUY if signal.signal_type == SignalType.LONG else Direction.SELL
        if direction == Direction.BUY:
            max_affordable = int(self.portfolio.cash // price)
            quantity = min(quantity, max_affordable)

            if quantity == 0:
                logger.warning(f"[{signal.symbol}] BUY REJECTED: Insufficient cash (£{self.portfolio.cash:.2f}) at price £{price:.2f}.")
                return

        logger.info(f"[{signal.symbol}] ORDER CREATED (T+1): {direction} {quantity} shares @ £{price:.2f}")

        order = OrderEvent(symbol=signal.symbol, direction=direction, quantity=quantity)
        self.event_manager.publish("pending_orders", order)