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

## ✅ Step 2 — Pattern detection engine
`backend/engine/patterns/` — deterministic detectors for 8 candlestick patterns
(doji, hammer, shooting star, marubozu, bullish/bearish engulfing, morning/
evening star) from OHLC geometry, plus **honest follow-through stats** that
measure what each pattern actually did historically (often weaker than the
folklore). Sample-size guardrails flag thin results. `demo_patterns.py`.
**34 tests passing** (20 engine + 14 pattern). Did not touch Step 1 code.

## ✅ Step 2.5 — Landing page (frontend foundation)
`frontend/` — Next.js + TS + Tailwind. Public landing page for **Veridian**.
Signature element: real backtest results (one win, one loss) pulled from the
engine. Establishes the design system (palette, type, components) the app
screens will reuse. Type-checks clean.

## ✅ Step 3 — FastAPI layer
`backend/api/` — HTTP surface over the whole engine: `/health`, `/symbols`,
`/strategies`, `/bars/{symbol}`, `POST /backtest`, `/patterns/{symbol}`.
Pydantic schemas define the contract; a service layer adapts engine → API
without touching the engine. Honest `disclaimer` field on every analytical
response. **47 tests passing** (13 new API tests via TestClient). Run with
`uvicorn api.main:app --reload`; docs at `/docs`.

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
