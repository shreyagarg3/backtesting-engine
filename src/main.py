import argparse
from pathlib import Path

from backtester.utils.data_feed import DataFeed
from backtester.utils.event_manager import EventManager
from backtester.core.broker import Broker
from backtester.data.events import MarketEvent
from backtester.strategies.sma_crossover_strategy import SMACrossoverStrategy

project_root = Path(__file__).resolve().parents[2]


class SimulationEngine:
    def __init__(self, data_feed: DataFeed, event_manager: EventManager):
        self.data_feed = data_feed
        self.event_manager = event_manager

    def run(self):
        for bar in self.data_feed:
            # TO DO: Add support for multi-asset backtesting (hardcoded 'BTC' for now)
            self.event_manager.publish("market_bars", MarketEvent(symbol="BTC", bar=bar))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a backtest against historical market data.")
    parser.add_argument("-f", "--filename", required=True, help="Name of the CSV file (stored in output_data directory).")
    parser.add_argument("-i", "--initial-capital", type=float, default=100000.0, help="Initial cash balance.")
    parser.add_argument("-c", "--commission-per-share", type=float, default=0.005, help="The amount of commission to be paid per share bought/sold.")
    parser.add_argument("-s", "--slippage-perc", type=float, default=0.0005, help="The percentage in slippage applied per share bought/sold.")

    args = parser.parse_args()

    event_manager = EventManager()
    data_feed = DataFeed(project_root / "output_data" / args.filename)

    broker = Broker(
        event_manager=event_manager, 
        initial_capital=args.initial_capital,
        commission_per_share=args.commission_per_share, 
        slippage=args.slippage_perc
    )

    sma_crossover_strategy = SMACrossoverStrategy(
        event_manager=event_manager,
        fast_window=10,
        slow_window=50
    )

    engine = SimulationEngine(data_feed=data_feed, event_manager=event_manager)
    engine.run()