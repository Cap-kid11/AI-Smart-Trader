"""High-level tutor service.

Ties together the pre-written lessons and the live coach, assembling real
context (detected patterns, honest follow-through, the user's vocabulary) so
coaching is grounded and personalized. Falls back to pre-written content when
live coaching isn't available, so the tutor always responds.
"""
from __future__ import annotations

from pathlib import Path

from engine.annotations import label_summary
from engine.data import CsvDataAdapter
from engine.patterns import PATTERNS, detect_all, follow_through_all

from . import coach as _coach
from .lessons import CONCEPTS, LESSONS, get_concept, get_lesson

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data_samples"


def available() -> bool:
    return _coach.is_available()


def lesson_for(pattern_key: str) -> dict | None:
    return get_lesson(pattern_key)


def all_lessons() -> dict:
    return LESSONS


def concepts() -> dict:
    return CONCEPTS


def _asset_context(symbol: str, user_id: str | None) -> dict:
    """Assemble real context for grounding the coach."""
    ctx: dict = {"symbol": symbol}
    try:
        bars = CsvDataAdapter(DATA_DIR).get_bars(symbol)
    except FileNotFoundError:
        return ctx

    # recent detected patterns
    detected = detect_all(bars)
    hits = []
    for key in detected.columns:
        info = PATTERNS[key][1]
        for idx in detected.index[detected[key]]:
            hits.append({
                "date": idx.strftime("%Y-%m-%d"),
                "pattern_name": info.name,
                "bias": info.bias,
            })
    hits.sort(key=lambda h: h["date"])
    ctx["recent_patterns"] = hits[-8:]

    # honest follow-through
    ctx["follow_through"] = [
        {
            "pattern": f.pattern,
            "occurrences": f.occurrences,
            "pct_up": f.pct_up,
            "avg_return": f.avg_return,
            "horizon": f.horizon,
            "reliable_sample": f.reliable_sample,
        }
        for f in follow_through_all(bars, horizon=5)
    ]

    if user_id:
        ctx["vocabulary"] = label_summary(user_id)

    return ctx


def ask(
    question: str,
    symbol: str | None = None,
    user_id: str | None = None,
) -> dict:
    """Answer a learner question.

    Returns {"answer": str, "source": "ai"|"lessons", "live": bool}.
    Never raises for lack of a key — falls back to pre-written content.
    """
    context = _asset_context(symbol, user_id) if symbol else {}

    if _coach.is_available():
        try:
            answer = _coach.coach(question, context=context)
            return {"answer": answer, "source": "ai", "live": True}
        except Exception:
            pass  # fall through to pre-written content

    return {"answer": _fallback_answer(question), "source": "lessons", "live": False}


def _fallback_answer(question: str) -> str:
    """Best-effort answer from pre-written content when no live model.

    Matches the question against known pattern/concept keywords; otherwise
    returns the honest-limits concept as a sane default.
    """
    q = question.lower()
    # try to match a pattern by name
    for key, lesson in LESSONS.items():
        name = lesson["title"].lower()
        if key.replace("_", " ") in q or name in q:
            return (
                f"{lesson['title']}\n\n"
                f"What it is: {lesson['what']}\n\n"
                f"Why it matters: {lesson['why']}\n\n"
                f"Watch for: {lesson['watch_for']}"
            )
    # try concepts
    if "candle" in q:
        return CONCEPTS["candles"]
    if "follow" in q or "predict" in q or "work" in q:
        return CONCEPTS["follow_through"]

    return (
        "Live coaching isn't configured right now, but here's the most important "
        f"principle: {CONCEPTS['honest_limits']} Ask about a specific pattern "
        "(hammer, doji, engulfing, star) and I'll explain it."
    )
