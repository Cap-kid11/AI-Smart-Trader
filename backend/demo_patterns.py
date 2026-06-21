"""Demo: detect candlestick patterns and show HONEST follow-through stats.

    python demo_patterns.py

Shows what each pattern actually did historically on the sample data -- which
is often weaker than the tradition claims. That gap is the point.
"""
from pathlib import Path

from engine.data import CsvDataAdapter
from engine.patterns import PATTERNS, detect_all, follow_through_all

DATA_DIR = Path(__file__).resolve().parent / "data_samples"


def main():
    bars = CsvDataAdapter(DATA_DIR).get_bars("SAMPL")

    print("Patterns the engine can read:")
    for key, (_fn, info) in PATTERNS.items():
        print(f"  - {info.name} ({info.bias}, {info.candles}-candle)")

    print("\nDetected occurrences on SAMPL:")
    counts = detect_all(bars).sum().sort_values(ascending=False)
    for name, n in counts.items():
        print(f"  {name:<20} {int(n)}")

    print("\nHonest follow-through, 5 bars later (tradition vs reality):")
    print("-" * 64)
    for ft in follow_through_all(bars, horizon=5):
        print(" ", ft.summary())

    print(
        "\nNote: 'bullish'/'bearish' are TRADITIONAL labels. The percentages "
        "above are what actually happened on this data -- read them, not the "
        "folklore."
    )


if __name__ == "__main__":
    main()
