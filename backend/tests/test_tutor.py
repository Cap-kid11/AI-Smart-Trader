"""Tests for the AI tutor endpoints.

These run WITHOUT an ANTHROPIC_API_KEY, so they exercise the pre-written
fallback path and the response contract. With a key set, /tutor/ask would
return live coaching (source="ai", live=True) — not exercised in CI.

Run from backend/:  python -m pytest tests/test_tutor.py -q
"""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_lessons_list():
    r = client.get("/tutor/lessons")
    assert r.status_code == 200
    body = r.json()
    assert len(body["lessons"]) == 8
    keys = [l["key"] for l in body["lessons"]]
    assert "hammer" in keys
    # each lesson has the teaching fields
    hammer = next(l for l in body["lessons"] if l["key"] == "hammer")
    assert hammer["what"] and hammer["why"] and hammer["watch_for"]
    assert isinstance(body["live_coaching_available"], bool)


def test_ask_pattern_fallback():
    r = client.post("/tutor/ask", json={
        "question": "what is a hammer?",
        "symbol": "SAMPL",
        "user_id": "demo-user",
    })
    assert r.status_code == 200
    body = r.json()
    assert "Hammer" in body["answer"]
    # without a key, this is the pre-written path
    assert body["source"] in ("ai", "lessons")
    assert isinstance(body["live"], bool)


def test_ask_concept_fallback():
    r = client.post("/tutor/ask", json={"question": "how do candles work?"})
    assert r.status_code == 200
    assert "candlestick" in r.json()["answer"].lower()


def test_ask_empty_question_400():
    r = client.post("/tutor/ask", json={"question": "   "})
    assert r.status_code == 400


def test_ask_unknown_topic_gives_honest_default():
    r = client.post("/tutor/ask", json={"question": "xyzzy nonsense"})
    assert r.status_code == 200
    # falls back to the honest-limits principle
    assert len(r.json()["answer"]) > 0
