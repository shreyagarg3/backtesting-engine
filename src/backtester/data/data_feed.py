import csv
from pathlib import Path
from datetime import datetime

from .bar import Bar

class DataFeed:
    def __init__(self, filepath: Path):
        self._filepath = filepath
        self._file = None
        self._reader = None

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self) -> Bar:
        if self._reader is None:
            self._open()

        try:
            row = next(self._reader)
        except StopIteration:
            self.close()
            raise

        return self._parse_row(row)

    def _open(self):
        self._file = open(self._filepath, 'r', newline='')
        self._reader = csv.DictReader(self._file)

    def _parse_row(self, row: dict) -> Bar:
        return Bar(
            timestamp=datetime.fromisoformat(row["Timestamp"].replace("Z", "+00:00")),
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"])
        )

    def close(self):
        if self._file:
            self._file.close()
            self._file = None
            self._reader = None