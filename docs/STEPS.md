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

## ✅ Step 4 — Dashboard frontend
`frontend/app/dashboard/` — the backtest console. Typed API client
(`lib/api.ts`) calls the FastAPI backend. Users pick symbol + strategy, set
risk limits (capital per trade, stop, max capital, bail-out) via sliders, run
a backtest, and see a live equity chart (`EquityChart` with hover), honest
metrics grid, the disclaimer, and the full trade table. Reuses the landing
page's design system. Type-clean. Graceful "is the backend running?" error
state.

## ✅ Step 5 — Annotation store ("teach the AI")
Backend: `engine/annotations/` — SQLModel/SQLite store. Each tag captures the
user's label PLUS market context (OHLCV window + RSI/EMA/SMA at that candle),
turning tags into labeled examples. API routes: `POST /annotations`,
`GET /annotations/{user_id}`, `DELETE /annotations/{user_id}/{id}`, with a
per-user vocabulary count. Frontend: `app/studio/` — click a candle on a real
candlestick chart (`CandleChart`) to label it; amber dots mark labeled candles;
vocabulary + library views. Owner-scoped deletes. SQLite now → Postgres later by
changing the URL. **54 tests passing** (7 new annotation tests).

## ▢ Step 6 — AI tutor
Mix of pre-written lesson content (fundamentals) + live model API calls
(personalized coaching). Powers the 3-stage autonomy model:
1. AI trades user's chosen strategy →
2. AI + user co-pilot →
3. user trades independently.

---

## ✅ Step 6 — AI tutor
Backend: `engine/tutor/` — pre-written lessons for 8 patterns + concepts
(`lessons.py`), live coaching via Anthropic API (`coach.py`) with an honest,
no-advice system prompt, and a service that assembles real context (detected
patterns, honest follow-through, user vocabulary) and falls back to lessons
when no `ANTHROPIC_API_KEY` is set. API: `GET /tutor/lessons`,
`POST /tutor/ask`. Frontend: `app/learn/` — coaching chat (labels each answer
live vs lesson) + expandable lessons library. All four screens now
cross-linked. **59 tests passing** (5 new tutor tests, fallback-path). Key is
server-side only, never exposed to frontend.

### 3-stage autonomy — now realized
1. AI trades chosen strategy → dashboard + risk controls (Steps 1,4)
2. AI + user co-pilot → tutor coaches on real data + user's annotations (Steps 5,6)
3. User trades alone → tutor is built to teach independence, not dependence

## ✅ Step 7 — Paper trading (extension 1 of 4)
Backend: `engine/paper/` — simulated portfolio (Portfolio/Position/Order
SQLModel tables on the shared `engine/db.py` engine), buy/sell with cash &
share guardrails, avg-cost tracking, live-priced holdings, P&L, order history,
reset. API: `GET /paper/{user}`, `POST /paper/buy|sell`, `/paper/{user}/orders`,
`/paper/{user}/reset`. Frontend: `app/paper/` — account summary, trade ticket,
holdings, order history. All 5 screens cross-linked. Honest `disclaimer` on
every response. **69 tests passing** (10 new). Realizes autonomy Stage 1.

## ▢ Extension plan (one by one)
1. ✅ Paper trading — simulated portfolio
2. ✅ Auth + user accounts — `engine/auth/` (bcrypt + JWT, self-contained), API
   `/auth/signup|login|me` + protected `/me/*` routes, frontend AuthProvider +
   `/auth` login/signup page + session restore; paper/studio use the logged-in
   user, fall back to demo-user. 80 tests passing (11 new). Set JWT_SECRET in
   prod.
3. ✅ Real market data — `AlpacaDataAdapter` implemented (daily bars, disk
   cache, lazy SDK import) behind the existing `DataAdapter` interface. A
   provider factory (`engine/data/provider.py`) switches CSV↔Alpaca via
   `DATA_PROVIDER` env var and falls back to CSV if keys are missing. Services,
   paper store, and tutor all use the provider — zero engine changes proved the
   interface design. `/symbols` reports the active provider; dashboard shows a
   LIVE/SAMPLE badge. 86 tests passing (6 new). Needs free Alpaca keys to go live.
4. ✅ Deploy live — production config complete: backend `Dockerfile` +
   `railway.json` + `render.yaml` (with one-click Postgres), frontend
   `vercel.json`. CORS origins now env-configurable (`CORS_ORIGINS`); db layer
   normalizes `postgres://`→`postgresql+psycopg://` and psycopg added. Full
   step-by-step in `docs/DEPLOYMENT.md`. 86 tests passing. Actual deploy clicks
   are the owner's (accounts/credentials). NOTE: freelance — the live URL is the
   client-facing demo.

## Resume notes for the next session / Cursor
- Run `cd backend && python -m pytest -q` to confirm the engine is green.
- Run `python demo.py` to see it work end to end.
- Everything talks to the `DataAdapter` interface — swap CSV for Alpaca there.
- No real-money order execution is shipped. Paper/simulated only.
- No fixed win-rate promises anywhere. Metrics are reported honestly.
