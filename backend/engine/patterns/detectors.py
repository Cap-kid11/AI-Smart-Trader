"""Candlestick pattern detectors.

Each detector is a deterministic rule over OHLC values. Detection is reliable
because it's geometry, not prediction -- a hammer either meets the shape
criteria or it doesn't. What candles *predict* is a separate, honest question
answered by follow-through statistics (see stats.py), never asserted here.

Each detector returns a boolean Series aligned to the input bars: True on the
bar where the pattern completes.

Pattern types are tagged bullish / bearish / neutral by their *traditional*
reading. That tag is a label of convention, NOT a promise about what happens
next.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import candles as cd


@dataclass(frozen=True)
class PatternInfo:
    key: str
    name: str
    bias: str          # "bullish" | "bearish" | "neutral" (by convention)
    candles: int       # how many candles the pattern spans
    description: str


# --- Single-candle patterns ---

def doji(bars: pd.DataFrame, body_thresh: float = 0.1) -> pd.Series:
    """Open and close nearly equal: body is <=10% of the range. Indecision."""
    o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
    rng = (h - l).replace(0, pd.NA)
    frac = (c - o).abs() / rng
    return (frac <= body_thresh).fillna(False)


def hammer(bars: pd.DataFrame) -> pd.Series:
    """Small body near the top, long lower wick (>=2x body), little upper wick.

    Traditionally a bullish reversal signal when it appears after a decline.
    """
    out = []
    for o, h, l, c in zip(bars["open"], bars["high"], bars["low"], bars["close"]):
        b = cd.body(o, c)
        lw = cd.lower_wick(o, l, c)
        uw = cd.upper_wick(o, h, c)
        rng = cd.candle_range(h, l)
        if rng == 0 or b == 0:
            out.append(False)
            continue
        out.append(lw >= 2 * b and uw <= b and (b / rng) <= 0.4)
    return pd.Series(out, index=bars.index)


def shooting_star(bars: pd.DataFrame) -> pd.Series:
    """Mirror of the hammer: long upper wick, small body near the low.

    Traditionally a bearish reversal signal after an advance.
    """
    out = []
    for o, h, l, c in zip(bars["open"], bars["high"], bars["low"], bars["close"]):
        b = cd.body(o, c)
        lw = cd.lower_wick(o, l, c)
        uw = cd.upper_wick(o, h, c)
        rng = cd.candle_range(h, l)
        if rng == 0 or b == 0:
            out.append(False)
            continue
        out.append(uw >= 2 * b and lw <= b and (b / rng) <= 0.4)
    return pd.Series(out, index=bars.index)


def marubozu(bars: pd.DataFrame, wick_thresh: float = 0.05) -> pd.Series:
    """A candle that is almost all body -- tiny wicks. Strong conviction."""
    out = []
    for o, h, l, c in zip(bars["open"], bars["high"], bars["low"], bars["close"]):
        rng = cd.candle_range(h, l)
        if rng == 0:
            out.append(False)
            continue
        uw = cd.upper_wick(o, h, c)
        lw = cd.lower_wick(o, l, c)
        out.append((uw / rng) <= wick_thresh and (lw / rng) <= wick_thresh)
    return pd.Series(out, index=bars.index)


# --- Two-candle patterns ---

def bullish_engulfing(bars: pd.DataFrame) -> pd.Series:
    """A down candle followed by an up candle whose body engulfs it."""
    o, c = bars["open"], bars["close"]
    prev_bear = c.shift(1) < o.shift(1)
    curr_bull = c > o
    engulf = (o <= c.shift(1)) & (c >= o.shift(1))
    return (prev_bear & curr_bull & engulf).fillna(False)


def bearish_engulfing(bars: pd.DataFrame) -> pd.Series:
    """An up candle followed by a down candle whose body engulfs it."""
    o, c = bars["open"], bars["close"]
    prev_bull = c.shift(1) > o.shift(1)
    curr_bear = c < o
    engulf = (o >= c.shift(1)) & (c <= o.shift(1))
    return (prev_bull & curr_bear & engulf).fillna(False)


# --- Three-candle patterns ---

def morning_star(bars: pd.DataFrame) -> pd.Series:
    """Bearish candle, small-bodied middle, then a strong bullish candle.

    Traditional bullish reversal.
    """
    o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
    body1 = (c.shift(2) - o.shift(2))
    body3 = (c - o)
    rng2 = (h.shift(1) - l.shift(1)).replace(0, pd.NA)
    small_mid = ((c.shift(1) - o.shift(1)).abs() / rng2) <= 0.3
    first_bear = body1 < 0
    third_bull = body3 > 0
    # third closes back into the first candle's body (recovers the drop)
    recover = c >= (o.shift(2) + c.shift(2)) / 2
    return (first_bear & small_mid & third_bull & recover).fillna(False)


def evening_star(bars: pd.DataFrame) -> pd.Series:
    """Bullish candle, small-bodied middle, then a strong bearish candle.

    Traditional bearish reversal.
    """
    o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
    body1 = (c.shift(2) - o.shift(2))
    body3 = (c - o)
    rng2 = (h.shift(1) - l.shift(1)).replace(0, pd.NA)
    small_mid = ((c.shift(1) - o.shift(1)).abs() / rng2) <= 0.3
    first_bull = body1 > 0
    third_bear = body3 < 0
    decline = c <= (o.shift(2) + c.shift(2)) / 2
    return (first_bull & small_mid & third_bear & decline).fillna(False)


# Registry: key -> (detector fn, PatternInfo)
PATTERNS: dict[str, tuple] = {
    "doji": (doji, PatternInfo(
        "doji", "Doji", "neutral", 1,
        "Open and close are nearly equal — a candle of indecision where neither "
        "buyers nor sellers won the session.")),
    "hammer": (hammer, PatternInfo(
        "hammer", "Hammer", "bullish", 1,
        "Small body up top with a long lower wick: sellers pushed price down "
        "but buyers reclaimed it by the close.")),
    "shooting_star": (shooting_star, PatternInfo(
        "shooting_star", "Shooting Star", "bearish", 1,
        "Small body down low with a long upper wick: buyers pushed up but "
        "sellers rejected the highs by the close.")),
    "marubozu": (marubozu, PatternInfo(
        "marubozu", "Marubozu", "neutral", 1,
        "Almost pure body with tiny wicks — one side controlled the entire "
        "session, signalling strong conviction in that direction.")),
    "bullish_engulfing": (bullish_engulfing, PatternInfo(
        "bullish_engulfing", "Bullish Engulfing", "bullish", 2,
        "A down candle fully engulfed by the next up candle's body — buyers "
        "overwhelmed the prior selling.")),
    "bearish_engulfing": (bearish_engulfing, PatternInfo(
        "bearish_engulfing", "Bearish Engulfing", "bearish", 2,
        "An up candle fully engulfed by the next down candle's body — sellers "
        "overwhelmed the prior buying.")),
    "morning_star": (morning_star, PatternInfo(
        "morning_star", "Morning Star", "bullish", 3,
        "A down candle, a small indecisive candle, then a strong up candle — a "
        "classic three-bar bottoming sequence.")),
    "evening_star": (evening_star, PatternInfo(
        "evening_star", "Evening Star", "bearish", 3,
        "An up candle, a small indecisive candle, then a strong down candle — a "
        "classic three-bar topping sequence.")),
}


def detect_all(bars: pd.DataFrame) -> pd.DataFrame:
    """Run every detector. Returns a DataFrame of booleans, one column per
    pattern key, aligned to `bars`."""
    result = {}
    for key, (fn, _info) in PATTERNS.items():
        result[key] = fn(bars).reindex(bars.index).fillna(False)
    return pd.DataFrame(result, index=bars.index)
