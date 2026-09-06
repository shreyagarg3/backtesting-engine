# Multi-asset backtesting engine

An event-driven (kafka inspired) backtesting engine to develop and evaluate trading strategies against historical market data.

## Features

- **Event-Driven Architecture:** Clean kafka-like architecture using custom event queues (MarketEvent, SignalEvent, OrderEvent, FillEvent).
- **Portfolio & Risk Management:** Tracks dynamic positions, cash balances, real-time PnL, and total portfolio equity curves.
- **Simulated Execution & Brokerage:** Modular execution handler simulating market fills, slippage, and fee structures.
- **Custom Strategy Framework:** Extensible BaseStrategy abstract base class to implement technical indicators and signals. 
- **Data Ingestion & Fetcher:** Modules for parsing historical bar data (DataFeed) and automated fetching (MarketDataFetcher).  

## Getting Started

### Prerequisites
- Python 3.9+

### Running the environment

1. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Generate historical data**
Execute the main driver script to start the backtester with the default strategy:
```bash
python src/market_data/market_data_fetcher.py -u <api_endpoint> -sym BTC -tf 1Min -s 2022-01-01 -e 2022-01-30 -o output_data
```

#### CLI Arguments (market_data_fetcher.py)
- -u, --url: Market data API endpoint (Required)
- -sym, --symbol: Asset symbol (e.g., BTC or AAPL, default: BTC)
- -tf, --timeframe: Bar aggregation timeframe (e.g., 1Min, 5Min, 1Hour, default: 1Min)
- -s, --start: Start date formatted as YYYY-MM-DD (default: 2022-01-01)
- -e, --end: End date formatted as YYYY-MM-DD (default: 2022-01-30)
- -o, --output-data: Directory path to write output files (default: output_data)
- --symbol-format: Optional string template format (e.g., "{}/USD", default: None)

4. **Run Backtest Engine**
Execute the main driver script to start the backtester with the default strategy:
```bash
python src/main.py -f <asset_name>.csv -i 100000 -c 0.005 -s 0.0005
```

#### CLI Arguments (main.py)
- -f, --filename: Name of the CSV file stored in the output_data directory (Required)
- -i, --initial-capital: Starting cash balance for the portfolio (default: 100000.0)
- -c, --commission-per-share: Fixed commission rate per share bought or sold (default: 0.005)
- -s, --slippage-perc: Slippage percentage penalty applied per share transaction (default: 0.0005)

## Architecture

1. **Data Feed (`DataFeed`):** Iterates over OHLCV bars and pushes `MarketEvent` instances into the queue.
2. **Strategy (`BaseStrategy`):** Listens for `MarketEvent` ticks, evaluates signals, and emits `SignalEvent` objects.
3. **Portfolio (`Portfolio`):** Processes `SignalEvent` signals, checks capital limits, and dispatches `OrderEvent` orders.
4. **Execution (`ExecutionHandler`):** Intercepts `OrderEvent` instructions, models fill slippage, and generates `FillEvent` records to update portfolio cash and open positions.