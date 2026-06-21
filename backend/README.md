# Trading Platform — Backtest Engine (backend)

The core engine of the platform: define a strategy, run it over historical
equities data, and get **honest** performance metrics. Long-only, paper/simulated.

> This engine reports real results — including bad ones. It does **not** target
> or promise any fixed win rate. A strategy that loses money will show that it
> loses money. That honesty is the product.

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python generate_sample_data.py    # creates seeded sample CSVs (already included)
python demo.py                    # run preset strategies on sample data
python -m pytest -q               # run the test suite
```

## Structure

```
backend/
├── engine/
│   ├── data/          # DataAdapter interface: CSV (now) + Alpaca stub (later)
│   ├── indicators/    # SMA, EMA, RSI — pure, transparent functions
│   ├── strategies/    # Strategy base class + presets (RSI, MA crossover)
│   ├── risk/          # position sizing + stop logic
│   ├── patterns/      # candlestick detection + honest follow-through stats
│   └── backtest/      # the simulation engine + honest metrics
├── api/               # FastAPI layer exposing the engine over HTTP
├── data_samples/      # seeded sample OHLCV (reproducible, no API key)
├── tests/             # pytest suite
├── demo.py            # backtest example
├── demo_patterns.py   # pattern-reading example
└── generate_sample_data.py
```

## Design principles

- **Swappable data.** Everything talks to the `DataAdapter` interface. Swap the
  bundled CSV adapter for Alpaca/Polygon by changing one line — engines unchanged.
- **No lookahead.** Signals computed on a bar's close are executed at the *next*
  bar's open. This is the most common way backtests lie; the engine avoids it.
- **Faithful execution.** The engine runs *the user's chosen strategy's rules*.
  It never invents its own strategy or hidden edge.
- **Honest metrics.** Win rate, avg win/loss, profit factor, max drawdown, and
  annualized Sharpe — the metrics that expose a bad strategy, not just flatter it.

## Metrics reported

| Metric | What it tells you |
|---|---|
| Total return | overall P&L over the period |
| Win rate | fraction of trades that were profitable |
| Avg win / Avg loss | average size of winners vs losers |
| Profit factor | gross profit ÷ gross loss (>1 is net positive) |
| Max drawdown | worst peak-to-trough equity drop |
| Sharpe (annualized) | return per unit of volatility |

## User-set governance (you control the AI)

The `RiskConfig` gives the user direct control over how much the AI may trade
and when it must stop:

| Control | Meaning |
|---|---|
| `fraction_per_trade` | fraction of available cash to deploy per position |
| `stop_loss_pct` | per-position stop distance (None = off) |
| `max_capital_fraction` | hard ceiling on total capital ever deployed at once |
| `bail_out_drawdown_pct` | kill-switch: stop opening trades once equity drops this far below its start (None = off) |

```python
from engine.risk import RiskConfig

risk = RiskConfig(
    fraction_per_trade=0.5,      # use up to 50% of cash per trade
    max_capital_fraction=0.5,    # never have more than 50% deployed at once
    bail_out_drawdown_pct=0.10,  # bail out at -10%
)
```

When the bail-out triggers, the engine stops opening **new** positions; open
positions still close normally by signal or stop.

## The HTTP API

The FastAPI layer (`api/`) exposes the whole engine for the frontend:

```bash
cd backend
uvicorn api.main:app --reload     # http://localhost:8000
# interactive docs at http://localhost:8000/docs
```

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | service check |
| GET | `/symbols` | available sample symbols |
| GET | `/strategies` | preset strategies + descriptions |
| GET | `/bars/{symbol}` | OHLCV bars (for charting) |
| POST | `/backtest` | run a strategy, get honest metrics + equity curve + trades |
| GET | `/patterns/{symbol}` | detected candlestick patterns + honest follow-through stats |

Every analytical response carries a `disclaimer` field — honest framing is part
of the contract, not optional. `profit_factor` is clamped (inf → 999) for JSON
safety. CORS is open to `http://localhost:3000` (the Next.js dev server);
tighten for production.

## Reading candles (pattern engine)

Detects 8 classic candlestick patterns from OHLC geometry — detection is
near-perfect because it's rules, not prediction. Crucially, it reports **honest
follow-through stats**: what each pattern *actually* did historically, with
sample-size caveats, instead of repeating folklore.

```python
from engine.data import CsvDataAdapter
from engine.patterns import detect_all, follow_through_all

bars = CsvDataAdapter("data_samples").get_bars("SAMPL")

detect_all(bars)              # boolean DataFrame: one column per pattern
for ft in follow_through_all(bars, horizon=5):
    print(ft.summary())       # honest "X% closed higher 5 bars later, avg ..."
```

Run `python demo_patterns.py` to see it. The `bullish`/`bearish` tags are
*traditional* labels — the percentages tell you what really happened.

## Adding a strategy

Subclass `Strategy` and return a Series of target positions in `{-1, 0, 1}`:

```python
from engine.strategies.base import Strategy
import pandas as pd

class MyStrategy(Strategy):
    name = "My Strategy"
    def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
        # +1 long, 0 flat, -1 short
        return (bars["close"] > bars["close"].rolling(10).mean()).astype(float)
```

## Going live (later)

`engine/data/adapters.py` has an `AlpacaDataAdapter` stub. Install `alpaca-py`,
supply credentials, and return a `DatetimeIndex` OHLCV DataFrame. Alpaca also
provides a **paper-trading** API — the intended path for simulated execution
before any real-money consideration.

## Roadmap

See `../docs/ARCHITECTURE.md` for the full plan: pattern engine, annotation
("teach the AI") store, AI tutor, and the Next.js frontend.
