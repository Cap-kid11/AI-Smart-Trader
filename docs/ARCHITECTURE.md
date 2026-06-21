# Trading Platform — Architecture & Scope

**Owner:** Kidus Girmay
**Status:** v0.1 — initial scope
**First target:** US equities (stocks)

---

## 1. What this platform is (and isn't)

**Is:** a strategy-development and education platform for equities traders. Users
define trading strategies, backtest them against historical data with honest
metrics, get reliable candlestick-pattern detection, learn to read charts, and
trade in a **paper (simulated) account**. An assistive AI layer helps build
strategies in plain language, explains patterns, and coaches the user.

**Is not:** a guaranteed-accuracy signal service. The platform does **not**
promise a fixed win rate (e.g. "75%"). It reports whatever the real, out-of-sample
numbers are. It does not place live real-money orders — paper trading only in v1.

### Why no guaranteed win rate

A durable 75% market-direction accuracy is not a realistic engineering target —
top quant funds with enormous resources do not sustain that. A backtest showing
it almost always indicates lookahead bias, overfitting, or survivorship bias.
Promising a performance number you can't substantiate is also the kind of claim
that draws securities regulators. The product's honesty *is* its competitive
edge: rigorous tooling, not a black-box oracle.

### What actually helps a trader

Research is consistent that survival comes from **process and risk discipline**,
not magic signals. So the platform centers backtesting, honest metrics, position
sizing, and education — the things that prevent blow-ups.

---

## 2. System overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js + TypeScript + Tailwind)              │
│  - Charting + annotation UI                              │
│  - Strategy builder                                      │
│  - Backtest results dashboard                            │
│  - Paper-trading dashboard                               │
│  - Learning / tutoring UI                                │
└───────────────┬─────────────────────────────────────────┘
                │ REST / WebSocket
┌───────────────┴─────────────────────────────────────────┐
│  Backend (Python — FastAPI)                              │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │ Strategy Engine │  │ Backtest Engine  │               │
│  └─────────────────┘  └──────────────────┘               │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │ Pattern Engine  │  │ Risk Module      │               │
│  └─────────────────┘  └──────────────────┘               │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │ Annotation Store│  │ Paper Broker     │               │
│  └─────────────────┘  └──────────────────┘               │
│  ┌──────────────────────────────────────┐                │
│  │ AI Tutor (model API calls)           │                │
│  └──────────────────────────────────────┘                │
└───────────────┬─────────────────────────────────────────┘
                │
┌───────────────┴───────────┐   ┌─────────────────────────┐
│ Market Data Adapter        │   │ Database (Postgres)     │
│ (Alpaca / Polygon — swap.) │   │ users, strategies,      │
└────────────────────────────┘   │ annotations, backtests  │
                                 └─────────────────────────┘
```

---

## 3. Modules

### 3.1 Strategy Engine
Define strategies as rules over indicators (e.g. "buy when RSI < 30 and price
crosses above 20-EMA"). Rules compile to signals. Indicators computed with a
vetted library (`pandas-ta` / `ta-lib`).

### 3.2 Backtest Engine
Runs a strategy over historical bars and reports **honest** metrics:
win rate, avg win/loss, profit factor, max drawdown, Sharpe, exposure, and
**out-of-sample / walk-forward** results to guard against overfitting.

### 3.3 Pattern Engine (candle reading)
Deterministic detection of classic candlestick patterns (engulfing, doji,
hammer, star, etc.) from OHLC relationships — this part *can* be near-perfect
because it's rules, not prediction. For each detected pattern it shows **honest
historical follow-through stats** per asset, never a guaranteed outcome.

### 3.4 Annotation Store ("teach the AI")
Users tag candles/zones on charts ("bullish engulfing", "my setup"). Each label
is stored with full context (OHLCV window + indicator values). Builds a
per-user personalized pattern library. This is supervised labeling — the AI
learns the user's *style and vocabulary*, not a market-beating secret.

### 3.5 Risk Module
Position sizing, stop-loss logic, max exposure / per-trade risk limits. Threaded
through backtests and paper trading. The unglamorous core that protects sessions.

### 3.6 Paper Broker
Simulated order execution against live/historical prices. Tracks a virtual
portfolio, P&L, and trade history. **No real-money orders in v1.** A broker
adapter interface exists so a real broker *could* be added later — but live order
placement is implemented and owned by the project operator, not shipped blindly.

### 3.7 AI Tutor
Powered by a **mix**: pre-written lesson content for stable fundamentals (what a
hammer *is*), live model API calls for personalized contextual coaching ("why
this candle on AAPL resembles the setup you tagged last week"). Frames everything
as probabilistic, never as guaranteed calls.

---

## 4. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js, TypeScript, Tailwind | Kidus's stack; SSR + good charting ecosystem |
| Charting | lightweight-charts (TradingView) | purpose-built for candles |
| Backend | Python + FastAPI | quant/ML libraries live in Python; async |
| Indicators | pandas-ta / TA-Lib | vetted, standard |
| Data | Alpaca (free + paper API), Polygon (paid upgrade) | behind a swappable adapter |
| DB | PostgreSQL | relational data: users, strategies, trades |
| AI | Anthropic API (Claude) | tutoring + NL strategy building |

Data source sits behind an **adapter interface** so it can be swapped without
touching the engines.

---

## 5. Build order

1. **Strategy + Backtest Engine** — the foundation; answers "does this idea
   actually work?" before risking anything. Highest value to a trader.
2. **Charting + Pattern Engine** — reliable candle reading on top of the data layer.
3. **Annotation + AI Tutor** — personalization and education.
4. **Risk Module** — built alongside 1–3, central not optional.
5. **Paper Broker + dashboard** — simulated trading once signals are trustworthy.

---

## 6. Hard lines (non-negotiable)

- No fixed/guaranteed win-rate claims anywhere in product or marketing.
- No live real-money order execution shipped as a turnkey feature.
- No personalized investment advice — outputs are tools and information.
- All backtest metrics reported honestly, including out-of-sample.

---

## 7. Open questions / next decisions

- Exact equities data plan (Alpaca free tier history limits vs Polygon).
- Auth approach (NextAuth vs custom) when we add accounts.
- Hosting target (Vercel for frontend; Fly.io / Railway / Render for backend).
- Mobile: React Native vs responsive PWA (decide after web core is stable).
