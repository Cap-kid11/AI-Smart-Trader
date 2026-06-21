# Trading Platform

A strategy-development and education platform for equities traders. Define
strategies, backtest them with honest metrics, learn to read candlestick
patterns, and trade in a simulated (paper) account — with an assistive AI
layer that helps build strategies, explains patterns, and coaches you toward
trading independently.

**Author:** Kidus Girmay

## What this is

- Backtest your strategy ideas before risking anything, with **honest** metrics.
- Reliable candlestick-pattern detection (rules-based, near-perfect at *identifying*).
- Learn to read charts; teach the AI your own pattern vocabulary.
- Paper trading — simulated execution, no real-money orders.

## What this is not

- Not a guaranteed-accuracy signal service. No fixed win-rate promises.
- Not a black box that trades real money for you.
- Not personalized investment advice.

The honesty is the point — and the competitive edge.

## Layout

```
trading-platform/
├── docs/
│   └── ARCHITECTURE.md     # full system design & build plan
└── backend/
    └── ...                 # the backtest engine (see backend/README.md)
```

## Status

v0.1 — backtest engine complete (strategies, indicators, risk, honest metrics,
tests). Next: charting + pattern engine, then annotation + AI tutor, then the
Next.js frontend. See `docs/ARCHITECTURE.md`.

## Getting started

```bash
cd backend
pip install -r requirements.txt
python demo.py
```
