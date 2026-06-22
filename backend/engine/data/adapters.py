"""Market data adapters.

Everything in the engine talks to the `DataAdapter` interface, never to a
concrete data source. Swap CSV for Alpaca/Polygon by changing one line at
the call site -- the engines never change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}


class DataAdapter(ABC):
    """Contract every data source must satisfy."""

    @abstractmethod
    def get_bars(self, symbol: str) -> pd.DataFrame:
        """Return a DataFrame indexed by datetime with OHLCV columns."""
        raise NotImplementedError

    @staticmethod
    def _validate(df: pd.DataFrame) -> pd.DataFrame:
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"data missing required columns: {sorted(missing)}")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("data must be indexed by a DatetimeIndex")
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()
        return df


class CsvDataAdapter(DataAdapter):
    """Loads bars from local CSV files (the bundled sample data)."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"data dir not found: {self.data_dir}")

    def get_bars(self, symbol: str) -> pd.DataFrame:
        path = self.data_dir / f"{symbol}.csv"
        if not path.exists():
            raise FileNotFoundError(f"no sample file for symbol {symbol!r}: {path}")
        df = pd.read_csv(path, parse_dates=["date"]).set_index("date")
        df.columns = [c.lower() for c in df.columns]
        return self._validate(df)


class AlpacaDataAdapter(DataAdapter):
    """Live equities data via Alpaca (daily bars).

    Implements the same DataAdapter contract as CsvDataAdapter, so the engine,
    backtester, pattern detector, and paper trader use it without any change.

    Credentials come from constructor args or the ALPACA_API_KEY /
    ALPACA_SECRET_KEY environment variables. Never hardcode keys.

    Fetched bars are cached to disk (cache_dir) to respect Alpaca's rate limits
    and make repeat backtests fast. Delete the cache to force a refresh.
    """

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        cache_dir: str | Path | None = None,
        lookback_days: int = 1000,
        cache_ttl_hours: float = 12.0,
    ):
        import os

        self.api_key = api_key or os.environ.get("ALPACA_API_KEY")
        self.secret_key = secret_key or os.environ.get("ALPACA_SECRET_KEY")
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "Alpaca credentials missing. Set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY (or pass them in)."
            )
        self.lookback_days = lookback_days
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_dir = Path(cache_dir or Path(__file__).resolve().parent.parent.parent / ".bar_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, symbol: str) -> Path:
        return self.cache_dir / f"alpaca_{symbol.upper()}.csv"

    def _cache_fresh(self, path: Path) -> bool:
        if not path.exists():
            return False
        import time

        age_hours = (time.time() - path.stat().st_mtime) / 3600
        return age_hours < self.cache_ttl_hours

    def get_bars(self, symbol: str) -> pd.DataFrame:
        symbol = symbol.upper()
        cache = self._cache_path(symbol)

        if self._cache_fresh(cache):
            df = pd.read_csv(cache, parse_dates=["date"]).set_index("date")
            return self._validate(df)

        df = self._fetch(symbol)
        # write cache (reset index so 'date' is a column)
        df.reset_index().rename(columns={"index": "date"}).to_csv(cache, index=False)
        return self._validate(df)

    def _fetch(self, symbol: str) -> pd.DataFrame:
        """Fetch daily bars from Alpaca and shape them to the OHLCV contract."""
        from datetime import datetime, timedelta, timezone

        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        client = StockHistoricalDataClient(self.api_key, self.secret_key)
        start = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)

        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
        )
        bars = client.get_stock_bars(req)

        if symbol not in bars.data or not bars.data[symbol]:
            raise FileNotFoundError(f"Alpaca returned no bars for {symbol!r}")

        rows = [
            {
                "date": b.timestamp.replace(tzinfo=None),
                "open": float(b.open),
                "high": float(b.high),
                "low": float(b.low),
                "close": float(b.close),
                "volume": int(b.volume),
            }
            for b in bars.data[symbol]
        ]
        df = pd.DataFrame(rows).set_index("date")
        return df
