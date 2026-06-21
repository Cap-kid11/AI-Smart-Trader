# Veridian — Frontend

The web frontend for the trading platform, starting with the public landing
page. Next.js (App Router) + TypeScript + Tailwind.

## Run it

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

> Note: `npm install` may be slow on constrained networks. If it stalls, retry
> — the package set is standard (next, react, tailwind).

## What's here

- **Landing page** (`app/page.tsx`) — the public marketing page. Its signature
  element is a pair of **real backtest results from our own engine** (one
  winning, one losing). Showing the loss is intentional: honesty is the product.
- **Dashboard** (`app/dashboard/page.tsx`) — the backtest console. Pick a
  symbol and strategy, set your risk limits (capital per trade, stop loss, max
  capital deployed, bail-out threshold), run a backtest against the API, and see
  the equity curve, honest metrics, and the full trade list render live.
- **API client** (`lib/api.ts`) — typed client for the FastAPI backend.
- **Design system** (`tailwind.config.ts`, `app/globals.css`) — a serious
  "instrument" palette (deep slate, restrained amber accent, honest gain/loss
  green & red used only for real data). IBM Plex Sans + Mono.
- **Components** (`components/`) — `EquityChart` (full chart w/ hover),
  `MetricsGrid`, `Sparkline`, `ResultCard`.

## Connecting to the backend

The dashboard calls the FastAPI backend. Start it first:

```bash
cd ../backend
uvicorn api.main:app --reload   # serves http://localhost:8000
```

Set `NEXT_PUBLIC_API_BASE` (see `.env.example`) if your API runs elsewhere.
If the backend isn't running, the dashboard shows a clear message saying so.

## Brand

Product name: **Veridian** (veritas + the green of a market display). The whole
visual language rejects the hype-funnel look of typical trading-bot sites:
no fake guaranteed returns, no green-arrow theatrics — calm, credible, honest.

## Next

This landing page establishes the design system the app screens reuse:
charting view, strategy builder, risk controls, backtest dashboard. See
`../docs/STEPS.md`.
