import argparse
from pathlib import Path

from backtester.utils.data_feed import DataFeed
from backtester.utils.event_manager import EventManager
from backtester.core.execution_handler import ExecutionHandler

project_root = Path(__file__).resolve().parents[2]

class SimulationEngine:
    def __init__(self, data_feed: DataFeed, event_manager: EventManager):
        self.data_feed = data_feed
        self.event_manager = event_manager

    def run(self):
        print("Starting simulation loop...")

        for bar in self.data_feed:
            self.event_manager.publish("market_bars", {
                "type": "MARKET_BAR",
                "bar": bar
            })

        print("\n--- Backtest Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a backtest against historical market data.")
    parser.add_argument("-f", "--filename", required=True, help="Name of the CSV file (stored in output_data directory).")
    parser.add_argument("-i", "--initial-capital", type=float, default=100000.0, help="Initial cash balance.")
    parser.add_argument("-c", "--commission-per-share", type=float, default=0.005, help="The amount of commission to be paid per share bought/sold.")
    parser.add_argument("-s", "--slippage-perc", type=float, default=0.0005, help="The percentage in slippage applied per share bought/sold.")

    args = parser.parse_args()

    event_manager = EventManager()
    data_feed = DataFeed(project_root / "output_data" / args.filename)
    
    execution_handler = ExecutionHandler(
        event_manager=event_manager, 
        commission_per_share=args.commission_per_share, 
        slippage_pct=args.slippage_perc
    )

    engine = SimulationEngine(data_feed=data_feed, event_manager=event_manager)
    engine.run()