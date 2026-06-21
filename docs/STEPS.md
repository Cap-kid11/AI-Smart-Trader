# Build Plan — Step Tracker

Each step is a self-contained, tested, committable unit. Commit after each so
the project resumes cleanly across work sessions. ✅ = done, ▢ = pending.

---

## ✅ Step 0 — Architecture & scope
`docs/ARCHITECTURE.md`. Modules, stack, hard lines, build order.

## ✅ Step 1 — Backtest engine core
`backend/` — data adapter (CSV + Alpaca stub), indicators (SMA/EMA/RSI),
strategy interface + 2 presets, risk module, backtest engine with honest
metrics, demo, tests. **20 tests passing.**

Includes **user-set governance**: `max_capital_fraction` (cap on deployed
capital) and `bail_out_drawdown_pct` (kill-switch). User controls how much the
AI trades and when it bails.

## ▢ Step 2 — Pattern detection engine
Deterministic candlestick patterns (engulfing, doji, hammer, star, etc.) from
OHLC math. Honest historical follow-through stats per pattern per asset. This
is the "master at reading candles" piece — reliable at *identifying*, honest
about *predicting*.

## ▢ Step 3 — FastAPI layer
Expose the engine over HTTP: run backtests, list strategies, fetch bars +
detected patterns. The contract the frontend consumes.

## ▢ Step 4 — Next.js frontend
Charting (lightweight-charts), strategy builder, risk/governance controls,
backtest results dashboard. Kidus's stack: Next.js + TS + Tailwind.

## ▢ Step 5 — Annotation store ("teach the AI")
Users tag candles/zones; stored with full OHLCV + indicator context. Builds a
per-user personalized pattern library.

## ▢ Step 6 — AI tutor
Mix of pre-written lesson content (fundamentals) + live model API calls
(personalized coaching). Powers the 3-stage autonomy model:
1. AI trades user's chosen strategy →
2. AI + user co-pilot →
3. user trades independently.

---

## Resume notes for the next session / Cursor
- Run `cd backend && python -m pytest -q` to confirm the engine is green.
- Run `python demo.py` to see it work end to end.
- Everything talks to the `DataAdapter` interface — swap CSV for Alpaca there.
- No real-money order execution is shipped. Paper/simulated only.
- No fixed win-rate promises anywhere. Metrics are reported honestly.
