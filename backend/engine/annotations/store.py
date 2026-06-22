"""Annotation store — the "teach the AI" foundation.

A user tags a candle on a chart with a label ("my setup", "bullish engulfing",
"fakeout"). We don't just store the label — we capture the full market CONTEXT
at that candle: a window of OHLCV bars around it plus indicator values. That
turns each tag into a real labeled example, building a personalized pattern
library the AI tutor can later learn the user's vocabulary from.

Storage is SQLite via SQLModel for zero-setup local runs. Switch to Postgres
for production by changing the connection URL — the models don't change.

Nothing here trains a market-beating model. It captures supervised labels of
the user's own style, which is what "the AI learns how YOU read charts" means.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlmodel import Field, SQLModel, Session, create_engine, select

from engine.indicators import ema, rsi, sma


class Annotation(SQLModel, table=True):
    """One user-applied label on one candle, with captured market context."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    symbol: str = Field(index=True)
    date: str = Field(index=True)  # the candle's date, YYYY-MM-DD
    label: str  # the user's own term, e.g. "my setup", "bullish engulfing"
    note: str = ""  # optional free-text note
    # JSON-encoded context captured at annotation time:
    #   {"window": [{date,open,high,low,close,volume}, ...],
    #    "indicators": {"rsi14": .., "ema20": .., "sma50": ..}}
    context_json: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# --- Engine setup (SQLite by default) ---

DB_PATH = Path(__file__).resolve().parent.parent.parent / "veridian.db"
_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)


# Ensure the table exists as soon as the store is imported. create_all is
# idempotent, so this is safe to run on every import and guarantees the schema
# is present regardless of how the app is launched (uvicorn, TestClient, script).
init_db()


def _session() -> Session:
    return Session(_engine)


def capture_context(bars: pd.DataFrame, date: str, window: int = 7) -> dict:
    """Build the context payload for a candle: a surrounding OHLCV window plus
    indicator values at that candle. `date` must exist in `bars`."""
    if date not in {d.strftime("%Y-%m-%d") for d in bars.index}:
        raise KeyError(f"date {date!r} not in bars for context capture")

    # locate the integer position of the date
    dates = [d.strftime("%Y-%m-%d") for d in bars.index]
    idx = dates.index(date)

    lo = max(0, idx - window)
    hi = min(len(bars), idx + window + 1)
    win = bars.iloc[lo:hi]
    window_rows = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
            "volume": int(r.volume),
        }
        for d, r in win.iterrows()
    ]

    # indicator values at the annotated candle (NaN -> None for JSON)
    r14 = rsi(bars["close"], 14)
    e20 = ema(bars["close"], 20)
    s50 = sma(bars["close"], 50)

    def at(series):
        v = series.iloc[idx]
        return None if pd.isna(v) else round(float(v), 4)

    return {
        "window": window_rows,
        "indicators": {
            "rsi14": at(r14),
            "ema20": at(e20),
            "sma50": at(s50),
        },
    }


def add_annotation(
    user_id: str,
    symbol: str,
    date: str,
    label: str,
    note: str = "",
    context: dict | None = None,
) -> Annotation:
    ann = Annotation(
        user_id=user_id,
        symbol=symbol,
        date=date,
        label=label,
        note=note,
        context_json=json.dumps(context or {}),
    )
    with _session() as s:
        s.add(ann)
        s.commit()
        s.refresh(ann)
        return ann


def list_annotations(
    user_id: str, symbol: str | None = None
) -> list[Annotation]:
    with _session() as s:
        stmt = select(Annotation).where(Annotation.user_id == user_id)
        if symbol:
            stmt = stmt.where(Annotation.symbol == symbol)
        stmt = stmt.order_by(Annotation.date)
        return list(s.exec(stmt))


def delete_annotation(user_id: str, annotation_id: int) -> bool:
    """Delete one annotation, scoped to its owner. Returns True if removed."""
    with _session() as s:
        ann = s.get(Annotation, annotation_id)
        if ann is None or ann.user_id != user_id:
            return False
        s.delete(ann)
        s.commit()
        return True


def label_summary(user_id: str) -> dict[str, int]:
    """Count how often the user has used each label — the beginnings of their
    personal pattern vocabulary."""
    counts: dict[str, int] = {}
    for ann in list_annotations(user_id):
        counts[ann.label] = counts.get(ann.label, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))
