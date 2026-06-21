"""Veridian API.

Exposes the backend engine over HTTP for the frontend:
  GET  /health
  GET  /symbols
  GET  /strategies
  GET  /bars/{symbol}
  POST /backtest
  GET  /patterns/{symbol}

Run (from backend/):
    uvicorn api.main:app --reload
Interactive docs at http://localhost:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import services
from .schemas import (
    BacktestRequest,
    BacktestResponse,
    BarsResponse,
    PatternsResponse,
    StrategyList,
)

app = FastAPI(
    title="Veridian API",
    version="0.1.0",
    description=(
        "Honest strategy backtesting and candlestick analysis. No guaranteed "
        "returns; simulated/paper results only."
    ),
)

# The Next.js dev server runs on :3000. Tighten this allowlist for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Sample symbols available from the bundled CSV data.
SAMPLE_SYMBOLS = ["SAMPL", "TESTC", "DEMOX"]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "veridian-api", "version": "0.1.0"}


@app.get("/symbols")
def symbols() -> dict:
    return {"symbols": SAMPLE_SYMBOLS}


@app.get("/strategies", response_model=StrategyList)
def strategies() -> StrategyList:
    return StrategyList(strategies=services.list_strategies())


@app.get("/bars/{symbol}", response_model=BarsResponse)
def bars(symbol: str) -> BarsResponse:
    try:
        return BarsResponse(symbol=symbol, bars=services.get_bars(symbol))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for symbol {symbol!r}")


@app.post("/backtest", response_model=BacktestResponse)
def backtest(req: BacktestRequest) -> BacktestResponse:
    try:
        return services.run_backtest_service(
            symbol=req.symbol,
            strategy_key=req.strategy_key,
            starting_equity=req.starting_equity,
            risk=req.risk,
            params=req.params,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for symbol {req.symbol!r}")
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown strategy {req.strategy_key!r}")
    except (TypeError, ValueError) as e:
        # bad preset params or risk values
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/patterns/{symbol}", response_model=PatternsResponse)
def patterns(symbol: str, horizon: int = 5) -> PatternsResponse:
    if not 1 <= horizon <= 60:
        raise HTTPException(status_code=400, detail="horizon must be between 1 and 60")
    try:
        return services.get_patterns_service(symbol, horizon=horizon)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No data for symbol {symbol!r}")
