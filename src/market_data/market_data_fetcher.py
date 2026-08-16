import argparse
import csv
import requests
import os
import logging
from pathlib import Path

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/market_data_fetcher.log", level=logging.INFO)

project_root = Path(__file__).resolve().parents[2]

class MarketDataFetcher:
    def __init__(self, start_date: str, end_date: str, symbol: str, timeframe: str, base_url: str, output_data: str, symbol_format: str | None=None):
        self._columns = {
            "o": "Open",
            "h": "High",
            "l": "Low",
            "c": "Close",
            "v": "Volume",
            "t": "Timestamp",
        }

        self._start_date = start_date
        self._end_date = end_date
        self._symbol = symbol
        self._timeframe = timeframe
        self._base_url = base_url
        self.output_data = output_data
        self._symbol_format = symbol_format

        self._session = requests.Session()

    @property
    def formatted_symbol(self):
        return self._symbol_format.format(self._symbol) if self._symbol_format else self._symbol

    def build(self):
        output_dir = project_root / self.output_data
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self._symbol.lower()}.csv"

        logger.info(f"Writing market data to: {output_path}")

        with open(output_path, 'w', newline='') as df:
            writer = csv.writer(df)
            page_token = None
            first_page = True

            while True:
                response = self._fetch_page(page_token)
                bars = response.get("bars", {})
                ohlc_data = bars.get(self.formatted_symbol, [])

                self._write_to_csv(ohlc_data, writer, first_page)
                first_page = False

                page_token = response.get("next_page_token")
                if not page_token:
                    break

        logger.info(f"Finished writing market data for {self.formatted_symbol} to {output_path}")

    def _fetch_page(self, page_token: str | None=None):
        params = {
            "symbols": self.formatted_symbol,
            "timeframe": self._timeframe,
            "start": f"{self._start_date}T00:00:00Z",
            "end": f"{self._end_date}T00:00:00Z",
            "limit": 1000,
            "sort": "asc",
        }

        if page_token:
            params["page_token"] = page_token

        response = self._session.get(
            self._base_url,
            params=params,
            headers={"accept": "application/json"}
        )

        response.raise_for_status()
        logger.info(f"Received {response.status_code} with page token: {page_token}")
        return response.json()

    def _write_to_csv(self, ohlc_data, writer, first_page: bool):
        if first_page:
            writer.writerow(self._columns.values())

        for row in ohlc_data:
            filtered_row = [row[column] for column in self._columns]
            writer.writerow(filtered_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--start", help="Start date in YYYY-MM-DD", default="2022-01-01")
    parser.add_argument("-e", "--end", help="End date in YYYY-MM-DD", default="2022-01-30")
    parser.add_argument("-sym", "--symbol", help="Asset symbol, e.g. BTC or AAPL", default="BTC")
    parser.add_argument("-tf", "--timeframe", help="OHLC timeframe, e.g. 1Min, 5Min, 1Hour", default="1Min")
    parser.add_argument("-u", "--url", help="Market data API endpoint", required=True)
    parser.add_argument("-o", "--output-data", help="Output directory to store the data", default="output_data")
    parser.add_argument("--symbol-format", help='Optional symbol format, e.g. "{}/USD"', default=None)

    args = parser.parse_args()

    data_fetcher = MarketDataFetcher(
        start_date=args.start,
        end_date=args.end,
        symbol=args.symbol,
        timeframe=args.timeframe,
        base_url=args.url,
        symbol_format=args.symbol_format,
        output_data=args.output_data
    )

    data_fetcher.build()