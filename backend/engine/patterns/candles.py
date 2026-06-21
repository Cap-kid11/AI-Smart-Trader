"""Candle geometry helpers.

Small, transparent functions describing the shape of a single candle from its
OHLC values. Pattern detectors are built from these so the logic stays readable
and the AI tutor can explain exactly why a candle qualifies as a pattern.
"""
from __future__ import annotations

import pandas as pd


def body(o: float, c: float) -> float:
    """Absolute size of the real body."""
    return abs(c - o)


def upper_wick(o: float, h: float, c: float) -> float:
    return h - max(o, c)


def lower_wick(o: float, l: float, c: float) -> float:
    return min(o, c) - l


def candle_range(h: float, l: float) -> float:
    return h - l


def is_bullish(o: float, c: float) -> bool:
    return c > o


def is_bearish(o: float, c: float) -> bool:
    return c < o


def body_pct(o: float, h: float, l: float, c: float) -> float:
    """Body size as a fraction of the full high-low range (0..1)."""
    rng = candle_range(h, l)
    if rng == 0:
        return 0.0
    return body(o, c) / rng


def avg_body(bars: pd.DataFrame, end_idx: int, lookback: int = 10) -> float:
    """Average real-body size over the prior `lookback` candles.

    Used to judge whether a candle is 'long' or 'small' relative to recent
    context, rather than with an absolute threshold.
    """
    start = max(0, end_idx - lookback)
    window = bars.iloc[start:end_idx]
    if len(window) == 0:
        return 0.0
    return float((window["close"] - window["open"]).abs().mean())
