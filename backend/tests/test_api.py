"""API tests using FastAPI's TestClient (no running server needed).

Run from backend/:  python -m pytest tests/test_api.py -q
"""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_symbols():
    r = client.get("/symbols")
    assert r.status_code == 200
    assert "SAMPL" in r.json()["symbols"]


def test_strategies():
    r = client.get("/strategies")
    assert r.status_code == 200
    keys = [s["key"] for s in r.json()["strategies"]]
    assert "rsi_mean_reversion" in keys
    assert "ma_crossover" in keys


def test_bars():
    r = client.get("/bars/SAMPL")
    assert r.status_code == 200
    body = r.json()
    assert body["symbol"] == "SAMPL"
    assert len(body["bars"]) > 0
    bar = body["bars"][0]
    assert {"date", "open", "high", "low", "close", "volume"} <= set(bar.keys())


def test_bars_unknown_symbol_404():
    r = client.get("/bars/NOPE")
    assert r.status_code == 404


def test_backtest():
    r = client.post("/backtest", json={
        "symbol": "SAMPL",
        "strategy_key": "rsi_mean_reversion",
        "starting_equity": 10000,
        "risk": {"fraction_per_trade": 0.5, "stop_loss_pct": 0.05},
    })
    assert r.status_code == 200
    body = r.json()
    assert body["strategy"] == "RSI Mean Reversion"
    assert "metrics" in body
    assert 0.0 <= body["metrics"]["win_rate"] <= 1.0
    assert len(body["equity_curve"]) > 0
    assert "disclaimer" in body  # honest framing always present


def test_backtest_with_bail_out():
    r = client.post("/backtest", json={
        "symbol": "SAMPL",
        "strategy_key": "ma_crossover",
        "starting_equity": 10000,
        "risk": {"bail_out_drawdown_pct": 0.1},
    })
    assert r.status_code == 200


def test_backtest_unknown_strategy_400():
    r = client.post("/backtest", json={
        "symbol": "SAMPL",
        "strategy_key": "does_not_exist",
    })
    assert r.status_code == 400


def test_backtest_unknown_symbol_404():
    r = client.post("/backtest", json={
        "symbol": "NOPE",
        "strategy_key": "rsi_mean_reversion",
    })
    assert r.status_code == 404


def test_backtest_bad_risk_rejected():
    # fraction_per_trade > 1 should fail Pydantic validation (422)
    r = client.post("/backtest", json={
        "symbol": "SAMPL",
        "strategy_key": "rsi_mean_reversion",
        "risk": {"fraction_per_trade": 2.0},
    })
    assert r.status_code == 422


def test_patterns():
    r = client.get("/patterns/SAMPL")
    assert r.status_code == 200
    body = r.json()
    assert body["symbol"] == "SAMPL"
    assert len(body["follow_through"]) == 8  # 8 patterns
    assert "disclaimer" in body
    # each follow-through entry has the honesty fields
    ft = body["follow_through"][0]
    assert "reliable_sample" in ft
    assert "pct_up" in ft


def test_patterns_bad_horizon_400():
    r = client.get("/patterns/SAMPL?horizon=999")
    assert r.status_code == 400


def test_patterns_unknown_symbol_404():
    r = client.get("/patterns/NOPE")
    assert r.status_code == 404
