import argparse
from pathlib import Path

from backtester.data.data_feed import DataFeed

project_root = Path(__file__).resolve().parents[2]

class Engine:
    def __init__(self, data_feed: DataFeed):
        self.data_feed = data_feed

    def run(self):
        for bar in self.data_feed:
            print(bar)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a backtest against historical market data.")
    parser.add_argument("-f", "--filename", required=True, help="Name of the CSV file (stored in output_data directory).")

    args = parser.parse_args()
    data_feed = DataFeed(project_root / "output_data" / args.filename)

    engine = Engine(data_feed)
    engine.run()