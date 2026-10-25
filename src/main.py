import argparse
from pathlib import Path

from backtester.core.broker import Broker
from backtester.core.execution_handler import ExecutionHandler

from backtester.data.events import MarketEvent

from backtester.strategies.sma_crossover import SMACrossover
from backtester.strategies.bollinger_mean_reversion import BollingerMeanReversion
from backtester.strategies.stochastic_crossover import StochasticCrossover
from backtester.strategies.strategy import Strategy

from backtester.utils.performance import compute_sharpe_ratio, compute_max_drawdown, compute_volatility
from backtester.utils.logger import get_logger
from backtester.utils.data_feed import DataFeed
from backtester.utils.event_manager import EventManager

project_root = Path(__file__).resolve().parents[1]
logger = get_logger(__name__)


class SimulationEngine:
    def __init__(self, data_feed: DataFeed, event_manager: EventManager):
        self.data_feed = data_feed
        self.event_manager = event_manager

    def run(self):
        for bar in self.data_feed:
            # TO DO: Add support for multi-asset backtesting (hardcoded 'BTC' for now)
            self.event_manager.publish("market_bars", MarketEvent(symbol="BTC", bar=bar))

    def determine_strategy(self, strategy: str, event_manager: EventManager) -> Strategy:
        match strategy:
            case "sma":
                return SMACrossover(event_manager=event_manager, fast_window=10, slow_window=50)
            case "bb":
                return BollingerMeanReversion(event_manager=event_manager, window=50, num_std=2.0)
            case "sc":
                return StochasticCrossover(event_manager=event_manager, k_window=14, d_window=3)
            case _:
                raise ValueError(f"Unknown strategy specified: '{strategy}'. Choose from 'sma', 'bb', or 'sc'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a backtest against historical market data.")
    parser.add_argument("-s", "--strategy", required=True, help="Name of the strategy to backtest against. Choose from 'sma', 'bb', or 'sc'.")
    parser.add_argument("-f", "--filename", required=True, help="Name of the CSV file (stored in output_data directory).")
    parser.add_argument("-i", "--initial-capital", type=float, default=100000.0, help="Initial cash balance.")
    parser.add_argument("-c", "--commission-per-share", type=float, default=0.005, help="The amount of commission to be paid per share bought/sold.")
    parser.add_argument("-p", "--slippage-perc", type=float, default=0.0005, help="The percentage in slippage applied per share bought/sold.")
    parser.add_argument("-m", "--max-position-perc", type=float, default=0.30, help="The maximum portfolio allocation percentage allowed for a single position.")

    args = parser.parse_args()

    event_manager = EventManager()
    data_feed = DataFeed(project_root / "output_data" / args.filename)

    broker = Broker(
        event_manager=event_manager, 
        initial_capital=args.initial_capital,
        commission_per_share=args.commission_per_share, 
        slippage=args.slippage_perc
    )

    _ = ExecutionHandler(
        event_manager=event_manager, 
        portfolio=broker.portfolio, 
        max_position_perc=args.max_position_perc
    )

    engine = SimulationEngine(data_feed=data_feed, event_manager=event_manager)
    _ = engine.determine_strategy(args.strategy, event_manager)

    engine.run()

    total_return_gbp = broker.portfolio_value - broker.portfolio.initial_capital
    total_return_pct = (total_return_gbp / broker.portfolio.initial_capital) * 100.0
    holdings_value = broker.portfolio_value - broker.cash

    sharpe_ratio = compute_sharpe_ratio(broker.portfolio.equity_curve)
    max_drawdown = compute_max_drawdown(broker.portfolio.equity_curve)
    volatility = compute_volatility(broker.portfolio.equity_curve)

    logger.info("=" * 100)
    logger.info("BACKTEST COMPLETED - FINAL PORTFOLIO SUMMARY")
    logger.info("=" * 100)

    logger.info(f"Initial Capital    : £{broker.portfolio.initial_capital:,.2f}")
    logger.info(f"Final Total Equity : £{broker.portfolio_value:,.2f}")
    logger.info(f"Total Net Return   : £{total_return_gbp:+,.2f} ({total_return_pct:+.2f}%)")
    logger.info(f"Ending Cash        : £{broker.cash:,.2f}")
    logger.info(f"Ending Holdings    : £{holdings_value:,.2f}")
    logger.info(f"Sharpe Ratio       : {sharpe_ratio:.2f}")
    logger.info(f"Max Drawdown       : {max_drawdown:.2f}%")
    logger.info(f"Volatility         : {volatility:.2f}%")

    if broker.portfolio._positions:
        logger.info("Open Positions     :")
        for symbol, qty in broker.portfolio._positions.items():
            if qty != 0:
                logger.info(f"  - {symbol}: {qty:+d} shares")
    else:
        logger.info("Open Positions     : None (Flat)")

    logger.info("=" * 100)