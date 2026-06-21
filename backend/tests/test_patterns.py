"""Tests for the candlestick pattern engine.

Run from backend/:  python -m pytest -q
"""
from pathlib import Path

import pandas as pd
import pytest

from engine.data import CsvDataAdapter
from engine.patterns import (
    PATTERNS,
    bearish_engulfing,
    bullish_engulfing,
    detect_all,
    doji,
    follow_through,
    follow_through_all,
    hammer,
    shooting_star,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data_samples"


@pytest.fixture
def bars():
    return CsvDataAdapter(DATA_DIR).get_bars("SAMPL")


def _df(rows):
    """Build a tiny OHLCV frame from (o,h,l,c) tuples."""
    idx = pd.date_range("2024-01-01", periods=len(rows))
    data = {
        "open": [r[0] for r in rows],
        "high": [r[1] for r in rows],
        "low": [r[2] for r in rows],
        "close": [r[3] for r in rows],
        "volume": [1000] * len(rows),
    }
    return pd.DataFrame(data, index=idx)


# --- Detector correctness on hand-built candles ---

def test_doji_detects_equal_open_close():
    # open == close, with range -> doji
    df = _df([(100, 102, 98, 100)])
    assert bool(doji(df).iloc[0]) is True


def test_doji_rejects_big_body():
    df = _df([(100, 106, 99, 105)])
    assert bool(doji(df).iloc[0]) is False


def test_hammer_shape():
    # small body up top, long lower wick, tiny upper wick
    df = _df([(100, 101, 90, 100.5)])
    assert bool(hammer(df).iloc[0]) is True


def test_hammer_rejects_long_upper_wick():
    df = _df([(100, 112, 99, 100.5)])
    assert bool(hammer(df).iloc[0]) is False


def test_shooting_star_shape():
    # small body near the low, long upper wick, minimal lower wick
    df = _df([(100, 110, 99.8, 100.5)])
    assert bool(shooting_star(df).iloc[0]) is True


def test_bullish_engulfing():
    # candle 1 bearish (105->100), candle 2 bullish engulfs (99->106)
    df = _df([(105, 106, 99, 100), (99, 107, 98, 106)])
    assert bool(bullish_engulfing(df).iloc[1]) is True


def test_bearish_engulfing():
    df = _df([(100, 106, 99, 105), (106, 107, 99, 100)])
    assert bool(bearish_engulfing(df).iloc[1]) is True


def test_bullish_engulfing_first_bar_is_false():
    df = _df([(105, 106, 99, 100), (99, 107, 98, 106)])
    # first bar can never be an engulfing (needs a prior candle)
    assert bool(bullish_engulfing(df).iloc[0]) is False


# --- detect_all shape ---

def test_detect_all_columns(bars):
    det = detect_all(bars)
    assert set(det.columns) == set(PATTERNS.keys())
    assert len(det) == len(bars)
    assert det.dtypes.apply(lambda d: d == bool).all()


# --- Follow-through stats: honesty guardrails ---

def test_follow_through_basic(bars):
    ft = follow_through(bars, "doji", horizon=5)
    assert ft.occurrences >= 0
    assert 0.0 <= ft.pct_up <= 1.0
    assert ft.horizon == 5


def test_follow_through_unknown_pattern_raises(bars):
    with pytest.raises(KeyError):
        follow_through(bars, "not_a_pattern")


def test_small_sample_flagged():
    # 3 bars -> at most 0 forward windows at horizon 5 -> 0 occurrences, unreliable
    df = _df([(100, 102, 98, 100), (100, 101, 99, 100), (100, 103, 97, 101)])
    ft = follow_through(df, "doji", horizon=5)
    assert ft.reliable_sample is False


def test_follow_through_all_sorted(bars):
    results = follow_through_all(bars, horizon=5)
    counts = [r.occurrences for r in results]
    assert counts == sorted(counts, reverse=True)


def test_no_lookahead_in_forward_returns():
    """Forward return must use a FUTURE bar, never the current or past."""
    # strictly rising closes; a pattern on bar 0 measured at horizon 2 should be
    # positive because close grows.
    df = _df([(100, 101, 99, 100), (100, 101, 99, 110), (100, 101, 99, 120)])
    # force a known signal on bar 0 only
    import numpy as np
    from engine.patterns.stats import forward_returns
    sig = pd.Series([True, False, False], index=df.index)
    rets = forward_returns(df, sig, horizon=2)
    assert len(rets) == 1
    assert rets[0] == pytest.approx(120 / 100 - 1)
