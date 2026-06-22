"""Data provider factory.

One place decides which DataAdapter the whole app uses, controlled by the
DATA_PROVIDER env var:

    DATA_PROVIDER=csv      -> bundled sample CSVs (default; clone-and-run)
    DATA_PROVIDER=alpaca   -> live Alpaca data (needs ALPACA_API_KEY/SECRET_KEY)

If 'alpaca' is requested but credentials are missing, we fall back to CSV with a
warning rather than crashing — the app always runs.

Services call get_provider() instead of constructing an adapter directly, so the
data source is swappable without touching any engine or service logic.
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

from .adapters import AlpacaDataAdapter, CsvDataAdapter, DataAdapter

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data_samples"

# Symbols the live provider should recognize. With Alpaca, any real ticker works;
# this list is what the UI advertises by default.
LIVE_SYMBOLS = ["AAPL", "MSFT", "NVDA", "SPY", "TSLA"]
SAMPLE_SYMBOLS = ["SAMPL", "TESTC", "DEMOX"]

_cached_provider: DataAdapter | None = None
_cached_kind: str | None = None


def provider_kind() -> str:
    """Which provider is actually active ('csv' or 'alpaca'), after fallback."""
    get_provider()
    return _cached_kind or "csv"


def available_symbols() -> list[str]:
    return LIVE_SYMBOLS if provider_kind() == "alpaca" else SAMPLE_SYMBOLS


def get_provider() -> DataAdapter:
    """Return the active data adapter (cached). Falls back to CSV on any issue."""
    global _cached_provider, _cached_kind
    if _cached_provider is not None:
        return _cached_provider

    requested = os.environ.get("DATA_PROVIDER", "csv").lower()

    if requested == "alpaca":
        try:
            _cached_provider = AlpacaDataAdapter()
            _cached_kind = "alpaca"
            return _cached_provider
        except Exception as e:  # missing creds, SDK, etc.
            warnings.warn(
                f"DATA_PROVIDER=alpaca requested but unavailable ({e}); "
                "falling back to bundled sample data.",
                stacklevel=2,
            )

    _cached_provider = CsvDataAdapter(DATA_DIR)
    _cached_kind = "csv"
    return _cached_provider


def reset_provider() -> None:
    """Clear the cached provider (e.g. after changing env in tests)."""
    global _cached_provider, _cached_kind
    _cached_provider = None
    _cached_kind = None
