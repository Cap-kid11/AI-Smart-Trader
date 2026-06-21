"""API schemas — the request/response contracts the frontend codes against.

Kept separate from the engine so the HTTP surface is explicit and stable even
if engine internals change.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# --- Shared ---

class RiskParams(BaseModel):
    """User-set risk governance. Mirrors engine.risk.RiskConfig."""
    fraction_per_trade: float = Field(0.2, gt=0, le=1)
    stop_loss_pct: float | None = Field(0.05, gt=0, lt=1)
    max_capital_fraction: float = Field(1.0, gt=0, le=1)
    bail_out_drawdown_pct: float | None = Field(None, gt=0, lt=1)


# --- Strategies ---

class StrategyInfo(BaseModel):
    key: str
    name: str
    description: str


class StrategyList(BaseModel):
    strategies: list[StrategyInfo]


# --- Bars ---

class Bar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class BarsResponse(BaseModel):
    symbol: str
    bars: list[Bar]


# --- Backtest ---

class BacktestRequest(BaseModel):
    symbol: str = Field(..., examples=["SAMPL"])
    strategy_key: str = Field(..., examples=["rsi_mean_reversion"])
    starting_equity: float = Field(10_000, gt=0)
    risk: RiskParams = RiskParams()
    # optional preset parameter overrides (e.g. {"window": 14, "lower": 30})
    params: dict = Field(default_factory=dict)


class TradeOut(BaseModel):
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    shares: int
    reason: str
    pnl: float
    return_pct: float


class EquityPoint(BaseModel):
    date: str
    equity: float


class BacktestMetrics(BaseModel):
    total_return: float
    num_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe: float


class BacktestResponse(BaseModel):
    symbol: str
    strategy: str
    starting_equity: float
    ending_equity: float
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    trades: list[TradeOut]
    # honest, non-negotiable framing returned WITH every result
    disclaimer: str


# --- Patterns ---

class PatternHit(BaseModel):
    date: str
    pattern_key: str
    pattern_name: str
    bias: str


class FollowThroughOut(BaseModel):
    pattern: str
    bias: str
    occurrences: int
    horizon: int
    pct_up: float
    avg_return: float
    median_return: float
    reliable_sample: bool


class PatternsResponse(BaseModel):
    symbol: str
    hits: list[PatternHit]
    follow_through: list[FollowThroughOut]
    disclaimer: str
