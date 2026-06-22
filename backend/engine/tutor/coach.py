"""Live AI coaching — the model-call half of the tutor.

Personalized, contextual coaching grounded in real platform data: the patterns
actually detected on an asset, their honest follow-through stats, and the user's
own annotation vocabulary. The model explains and teaches; it never invents a
market edge or gives buy/sell calls.

Design choices:
- The API key comes from the ANTHROPIC_API_KEY environment variable. Never
  hardcoded, never sent to the frontend.
- If no key is set (or the SDK/network is unavailable), callers fall back to the
  pre-written lessons. The app must never break for lack of a key.
- The system prompt hard-codes the honest framing and the no-advice rule.
"""
from __future__ import annotations

import os

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are the candlestick tutor inside Veridian, a trading-education tool.

Your job is to TEACH a trader to read charts themselves — and ultimately to not \
need you. You are a patient instructor, not a signal service.

Hard rules you must always follow:
- Never give buy/sell/hold recommendations or price targets. You explain; the \
user decides.
- Never claim a pattern predicts the future or cite any guaranteed win rate. A \
pattern's "bullish"/"bearish" name is a traditional label, not a forecast.
- When follow-through statistics are provided, ground your explanation in those \
real numbers, and point out honestly when they contradict the folklore or when \
the sample is too small to trust.
- Be concise and concrete. Prefer plain language over jargon, and explain any \
term you use.
- If the user has their own labels/vocabulary, use their words and connect new \
ideas to what they've already tagged.

You are helping the user build genuine skill and independence."""


def is_available() -> bool:
    """True if a live model call can be attempted."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def coach(
    question: str,
    context: dict | None = None,
    max_tokens: int = 700,
) -> str:
    """Answer a learning question with live coaching.

    `context` may include: symbol, detected patterns, follow-through stats, and
    the user's vocabulary. Raises RuntimeError if no key/SDK — callers should
    catch and fall back to pre-written content.
    """
    if not is_available():
        raise RuntimeError("Live coaching unavailable (no ANTHROPIC_API_KEY or SDK).")

    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    user_content = _build_user_message(question, context or {})

    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    # Concatenate text blocks.
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip()


def _build_user_message(question: str, context: dict) -> str:
    lines = [f"Learner's question: {question}", ""]

    symbol = context.get("symbol")
    if symbol:
        lines.append(f"They're looking at: {symbol}")

    patterns = context.get("recent_patterns")
    if patterns:
        lines.append("\nPatterns recently detected on this asset:")
        for p in patterns[:8]:
            lines.append(f"  - {p.get('pattern_name')} on {p.get('date')} "
                         f"(traditional bias: {p.get('bias')})")

    ft = context.get("follow_through")
    if ft:
        lines.append("\nHONEST follow-through stats on this asset (what actually "
                     "happened, not folklore):")
        for f in ft[:8]:
            sample = "" if f.get("reliable_sample") else " [small sample — unreliable]"
            lines.append(
                f"  - {f.get('pattern')}: {f.get('occurrences')} occurrences, "
                f"{f.get('pct_up', 0) * 100:.0f}% closed higher "
                f"{f.get('horizon')} bars later, avg {f.get('avg_return', 0) * 100:+.2f}%{sample}"
            )

    vocab = context.get("vocabulary")
    if vocab:
        terms = ", ".join(f"{k} (×{v})" for k, v in list(vocab.items())[:12])
        lines.append(f"\nThe learner's own labels so far: {terms}")
        lines.append("Use their vocabulary where it helps them connect ideas.")

    return "\n".join(lines)
