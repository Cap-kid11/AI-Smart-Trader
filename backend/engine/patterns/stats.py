"""Honest pattern follow-through statistics.

Detecting a pattern is reliable geometry. What a pattern *predicts* is an
empirical question -- so we measure it, on the actual data, instead of repeating
folklore. For each detected occurrence we look forward N bars and record the
return. The aggregate tells the user what really tended to happen after this
pattern on this instrument -- which is often far weaker than the tradition
claims, and that's exactly what the user deserves to know.

Nothing here is a prediction or a recommendation. It is a description of the
past, with the sample size shown so the user can judge how much to trust it.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from .detectors import PATTERNS


@dataclass
class FollowThrough:
    pattern: str
    bias: str
    occurrences: int
    horizon: int
    pct_up: float          # fraction of times price was higher N bars later
    avg_return: float      # mean forward return
    median_return: float
    # honesty guardrail: with few occurrences, stats mean little
    reliable_sample: bool

    def as_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        if self.occurrences == 0:
            return f"{self.pattern}: not found in this data."
        caveat = "" if self.reliable_sample else "  (small sample — treat with caution)"
        return (
            f"{self.pattern}: {self.occurrences} occurrences. "
            f"{self.pct_up:.0%} closed higher {self.horizon} bars later, "
            f"avg {self.avg_return:+.2%}.{caveat}"
        )


def forward_returns(bars: pd.DataFrame, signal: pd.Series, horizon: int) -> np.ndarray:
    """Forward close-to-close returns `horizon` bars after each True in signal."""
    close = bars["close"].values
    idx = np.where(signal.values)[0]
    rets = []
    for i in idx:
        j = i + horizon
        if j < len(close) and close[i] != 0:
            rets.append(close[j] / close[i] - 1)
    return np.array(rets)


def follow_through(
    bars: pd.DataFrame,
    pattern_key: str,
    horizon: int = 5,
    min_sample: int = 20,
) -> FollowThrough:
    """Compute honest follow-through stats for one pattern on these bars."""
    if pattern_key not in PATTERNS:
        raise KeyError(f"unknown pattern: {pattern_key!r}")
    fn, info = PATTERNS[pattern_key]
    signal = fn(bars).reindex(bars.index).fillna(False)
    rets = forward_returns(bars, signal, horizon)

    if len(rets) == 0:
        return FollowThrough(
            pattern=info.name, bias=info.bias, occurrences=0, horizon=horizon,
            pct_up=0.0, avg_return=0.0, median_return=0.0, reliable_sample=False,
        )

    return FollowThrough(
        pattern=info.name,
        bias=info.bias,
        occurrences=int(len(rets)),
        horizon=horizon,
        pct_up=float((rets > 0).mean()),
        avg_return=float(rets.mean()),
        median_return=float(np.median(rets)),
        reliable_sample=len(rets) >= min_sample,
    )


def follow_through_all(
    bars: pd.DataFrame,
    horizon: int = 5,
    min_sample: int = 20,
) -> list[FollowThrough]:
    """Follow-through stats for every pattern, sorted by occurrence count."""
    results = [
        follow_through(bars, key, horizon=horizon, min_sample=min_sample)
        for key in PATTERNS
    ]
    return sorted(results, key=lambda r: r.occurrences, reverse=True)
