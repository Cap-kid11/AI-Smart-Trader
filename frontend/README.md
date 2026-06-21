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
- **Design system** (`tailwind.config.ts`, `app/globals.css`) — a serious
  "instrument" palette (deep slate, restrained amber accent, honest gain/loss
  green & red used only for real data). IBM Plex Sans + Mono.
- **Components** (`components/`) — `Sparkline` (equity curves), `ResultCard`
  (honest metrics display).
- **Data** (`lib/backtest-data.ts`) — real numbers exported from the backtest
  engine. Regenerate from the engine; don't hand-edit.

## Brand

Product name: **Veridian** (veritas + the green of a market display). The whole
visual language rejects the hype-funnel look of typical trading-bot sites:
no fake guaranteed returns, no green-arrow theatrics — calm, credible, honest.

## Next

This landing page establishes the design system the app screens reuse:
charting view, strategy builder, risk controls, backtest dashboard. See
`../docs/STEPS.md`.
