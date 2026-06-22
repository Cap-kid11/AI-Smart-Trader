"""Pre-written lesson content — the stable fundamentals.

These don't need a model call: what a hammer *is* doesn't change. The live AI
layer (coach.py) handles personalized, contextual coaching on top of this.

Every lesson keeps the honest framing: a pattern's traditional bias is a label,
not a prediction. What it actually did is an empirical question the platform
answers with data.
"""
from __future__ import annotations

# Keyed by the same pattern keys used in engine.patterns.
LESSONS: dict[str, dict] = {
    "doji": {
        "title": "The Doji",
        "what": (
            "A doji forms when the open and close are almost identical, leaving "
            "a tiny or non-existent body. The session moved around but ended "
            "roughly where it began."
        ),
        "why": (
            "It signals indecision — neither buyers nor sellers took control. "
            "After a strong trend, that balance can hint the trend is tiring, "
            "but on its own a doji is a question, not an answer."
        ),
        "watch_for": (
            "Context matters more than the candle. A doji after a long rally "
            "means something different than one in the middle of a quiet range."
        ),
    },
    "hammer": {
        "title": "The Hammer",
        "what": (
            "A small body near the top of the range with a long lower wick at "
            "least twice the body, and little or no upper wick."
        ),
        "why": (
            "Sellers drove price down during the session, but buyers fought "
            "back and closed near the open. Traditionally read as a potential "
            "bullish reversal when it appears after a decline."
        ),
        "watch_for": (
            "'Traditionally bullish' is folklore until you check the data. On "
            "many instruments hammers are followed by an up move far less than "
            "half the time — always read the follow-through stats."
        ),
    },
    "shooting_star": {
        "title": "The Shooting Star",
        "what": (
            "The hammer's mirror: a small body near the low with a long upper "
            "wick and little lower wick."
        ),
        "why": (
            "Buyers pushed price up but sellers rejected the highs by the "
            "close. Traditionally a potential bearish reversal after an advance."
        ),
        "watch_for": (
            "As with the hammer, the traditional bias is a starting hypothesis, "
            "not a forecast. Check what actually followed it on this asset."
        ),
    },
    "marubozu": {
        "title": "The Marubozu",
        "what": (
            "A candle that is almost all body with tiny wicks — price opened at "
            "one extreme and closed at the other."
        ),
        "why": (
            "One side controlled the entire session, which reads as strong "
            "conviction in that direction."
        ),
        "watch_for": (
            "Strong conviction in a session doesn't guarantee continuation. "
            "Pair it with the broader trend and volume before concluding much."
        ),
    },
    "bullish_engulfing": {
        "title": "Bullish Engulfing",
        "what": (
            "A two-candle pattern: a down candle followed by an up candle whose "
            "body completely engulfs the prior body."
        ),
        "why": (
            "Buyers didn't just show up — they overwhelmed the previous "
            "session's selling. A classic potential bullish reversal."
        ),
        "watch_for": (
            "Bigger engulfing on higher volume tends to carry more weight, but "
            "the only honest test is the historical follow-through."
        ),
    },
    "bearish_engulfing": {
        "title": "Bearish Engulfing",
        "what": (
            "A down candle whose body fully engulfs the prior up candle's body."
        ),
        "why": (
            "Sellers overwhelmed the prior buying — a classic potential bearish "
            "reversal."
        ),
        "watch_for": (
            "Same caution as its bullish twin: the label is a hypothesis. Let "
            "the data tell you whether it meant anything here."
        ),
    },
    "morning_star": {
        "title": "The Morning Star",
        "what": (
            "A three-candle bottoming sequence: a down candle, a small "
            "indecisive candle, then a strong up candle."
        ),
        "why": (
            "It tells a story of selling, then balance, then buyers taking "
            "over — a potential bullish reversal at a low."
        ),
        "watch_for": (
            "Three-candle patterns are rarer, so you'll have fewer historical "
            "examples — be extra wary of small-sample follow-through stats."
        ),
    },
    "evening_star": {
        "title": "The Evening Star",
        "what": (
            "A three-candle topping sequence: an up candle, a small indecisive "
            "candle, then a strong down candle."
        ),
        "why": (
            "Buying, then balance, then sellers taking over — a potential "
            "bearish reversal at a high."
        ),
        "watch_for": (
            "Like the morning star, occurrences are few. Treat thin follow-"
            "through numbers as suggestive at best."
        ),
    },
}


# General concepts, not tied to one pattern.
CONCEPTS: dict[str, str] = {
    "candles": (
        "A candlestick summarizes one period of trading with four prices: open, "
        "high, low, close. The body spans open to close; the wicks reach to the "
        "high and low. Green/up means close above open; red/down the reverse. "
        "Reading candles is reading the tug-of-war between buyers and sellers."
    ),
    "follow_through": (
        "Follow-through means measuring what actually happened after a pattern "
        "appeared — e.g. how often price was higher five bars later. It's how "
        "you separate patterns that work on an asset from folklore that doesn't."
    ),
    "honest_limits": (
        "No candle predicts the future. Patterns shift the odds slightly at "
        "best, and those odds vary by asset and regime. Anyone promising a "
        "fixed win rate from candles is selling something."
    ),
}


def get_lesson(pattern_key: str) -> dict | None:
    return LESSONS.get(pattern_key)


def get_concept(key: str) -> str | None:
    return CONCEPTS.get(key)
