"""Tests for the data provider factory and Alpaca adapter.

These don't hit the Alpaca network — they test the switching logic, fallback
behavior, and that the Alpaca adapter validates credentials. Live fetching is
exercised manually with real keys.

Run from backend/:  python -m pytest tests/test_provider.py -q
"""
import os

import pytest

from engine.data import (
    AlpacaDataAdapter,
    CsvDataAdapter,
    available_symbols,
    get_provider,
    provider_kind,
    reset_provider,
)


@pytest.fixture(autouse=True)
def _clean_provider():
    reset_provider()
    yield
    reset_provider()


def test_default_is_csv(monkeypatch):
    monkeypatch.delenv("DATA_PROVIDER", raising=False)
    reset_provider()
    assert provider_kind() == "csv"
    assert isinstance(get_provider(), CsvDataAdapter)


def test_sample_symbols_in_csv_mode(monkeypatch):
    monkeypatch.delenv("DATA_PROVIDER", raising=False)
    reset_provider()
    syms = available_symbols()
    assert "SAMPL" in syms


def test_alpaca_without_keys_falls_back_to_csv(monkeypatch):
    monkeypatch.setenv("DATA_PROVIDER", "alpaca")
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)
    reset_provider()
    # should warn and fall back, never crash
    with pytest.warns(UserWarning):
        kind = provider_kind()
    assert kind == "csv"


def test_alpaca_adapter_requires_credentials(monkeypatch):
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)
    with pytest.raises(ValueError):
        AlpacaDataAdapter()


def test_alpaca_adapter_accepts_explicit_keys(tmp_path):
    # constructing with keys should succeed (no network call yet)
    a = AlpacaDataAdapter(
        api_key="fake", secret_key="fake", cache_dir=tmp_path
    )
    assert a.api_key == "fake"
    assert a.cache_dir.exists()


def test_provider_is_cached(monkeypatch):
    monkeypatch.delenv("DATA_PROVIDER", raising=False)
    reset_provider()
    p1 = get_provider()
    p2 = get_provider()
    assert p1 is p2  # same instance, not rebuilt
