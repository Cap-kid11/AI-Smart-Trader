"""Service layer: turns engine objects into API response shapes.

Keeps route handlers thin and keeps all engine-to-HTTP translation in one place.
The engine is never modified — this only adapts it.
"""
from __future__ import annotations

from pathlib import Path

from engine.data import CsvDataAdapter
from engine.patterns import PATTERNS, detect_all, follow_through_all
from engine.risk import RiskConfig
from engine.strategies import PRESETS
from engine.backtest import run_backtest

from .schemas import (
    Bar,
    BacktestMetrics,
    BacktestResponse,
    EquityPoint,
    FollowThroughOut,
    PatternHit,
    PatternsResponse,
    RiskParams,
    StrategyInfo,
    TradeOut,
)

# Honest framing returned with every analytical result. Non-negotiable.
BACKTEST_DISCLAIMER = (
    "Past performance does not predict future results. These are simulated "
    "results on historical data, not a recommendation. No guaranteed returns."
)
PATTERN_DISCLAIMER = (
    "'Bullish'/'bearish' are traditional labels. The follow-through numbers "
    "show what actually happened historically on this data — read those, not "
    "the folklore. Small samples are unreliable."
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data_samples"


def _adapter() -> CsvDataAdapter:
    return CsvDataAdapter(DATA_DIR)


def _friendly_strategy_name(key: str) -> str:
    cls = PRESETS.get(key)
    return cls().name if cls else key


def list_strategies() -> list[StrategyInfo]:
    out = []
    for key, cls in PRESETS.items():
        inst = cls()
        out.append(StrategyInfo(key=key, name=inst.name, description=inst.describe()))
    return out


def get_bars(symbol: str) -> list[Bar]:
    bars = _adapter().get_bars(symbol)
    return [
        Bar(
            date=idx.strftime("%Y-%m-%d"),
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=int(row.volume),
        )
        for idx, row in bars.iterrows()
    ]


def run_backtest_service(
    symbol: str,
    strategy_key: str,
    starting_equity: float,
    risk: RiskParams,
    params: dict,
) -> BacktestResponse:
    if strategy_key not in PRESETS:
        raise KeyError(strategy_key)

    bars = _adapter().get_bars(symbol)
    strategy = PRESETS[strategy_key](**params)
    risk_config = RiskConfig(
        fraction_per_trade=risk.fraction_per_trade,
        stop_loss_pct=risk.stop_loss_pct,
        max_capital_fraction=risk.max_capital_fraction,
        bail_out_drawdown_pct=risk.bail_out_drawdown_pct,
    )
    result = run_backtest(bars, strategy, risk=risk_config, starting_equity=starting_equity)

    equity_curve = [
        EquityPoint(date=idx.strftime("%Y-%m-%d"), equity=round(float(v), 2))
        for idx, v in result.equity_curve.items()
    ]
    trades = [
        TradeOut(
            entry_date=t.entry_date.strftime("%Y-%m-%d"),
            exit_date=t.exit_date.strftime("%Y-%m-%d"),
            entry_price=round(t.entry_price, 2),
            exit_price=round(t.exit_price, 2),
            shares=t.shares,
            reason=t.reason,
            pnl=round(t.pnl, 2),
            return_pct=round(t.return_pct, 4),
        )
        for t in result.trades
    ]
    m = result.metrics
    # profit_factor can be inf; clamp for JSON safety.
    pf = m["profit_factor"]
    if pf == float("inf"):
        pf = 999.0

    return BacktestResponse(
        symbol=symbol,
        strategy=strategy.name,
        starting_equity=round(result.starting_equity, 2),
        ending_equity=round(result.ending_equity, 2),
        metrics=BacktestMetrics(
            total_return=round(m["total_return"], 4),
            num_trades=m["num_trades"],
            win_rate=round(m["win_rate"], 4),
            avg_win=round(m["avg_win"], 4),
            avg_loss=round(m["avg_loss"], 4),
            profit_factor=round(pf, 2),
            max_drawdown=round(m["max_drawdown"], 4),
            sharpe=round(m["sharpe"], 2),
        ),
        equity_curve=equity_curve,
        trades=trades,
        disclaimer=BACKTEST_DISCLAIMER,
    )


def get_patterns_service(symbol: str, horizon: int = 5) -> PatternsResponse:
    bars = _adapter().get_bars(symbol)
    detected = detect_all(bars)

    hits: list[PatternHit] = []
    for key in detected.columns:
        info = PATTERNS[key][1]
        for idx in detected.index[detected[key]]:
            hits.append(
                PatternHit(
                    date=idx.strftime("%Y-%m-%d"),
                    pattern_key=key,
                    pattern_name=info.name,
                    bias=info.bias,
                )
            )
    hits.sort(key=lambda h: h.date)

    ft = [
        FollowThroughOut(
            pattern=f.pattern,
            bias=f.bias,
            occurrences=f.occurrences,
            horizon=f.horizon,
            pct_up=round(f.pct_up, 4),
            avg_return=round(f.avg_return, 4),
            median_return=round(f.median_return, 4),
            reliable_sample=f.reliable_sample,
        )
        for f in follow_through_all(bars, horizon=horizon)
    ]

    return PatternsResponse(
        symbol=symbol,
        hits=hits,
        follow_through=ft,
        disclaimer=PATTERN_DISCLAIMER,
    )
