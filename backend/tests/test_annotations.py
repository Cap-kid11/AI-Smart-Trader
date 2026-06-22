"""Tests for the annotation ("teach the AI") endpoints.

Uses unique user ids so runs don't collide in the shared SQLite db.
Run from backend/:  python -m pytest tests/test_annotations.py -q
"""
import uuid

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _uid() -> str:
    return f"test-{uuid.uuid4().hex[:8]}"


def _a_date() -> str:
    # a date known to exist in SAMPL sample data
    r = client.get("/bars/SAMPL")
    return r.json()["bars"][200]["date"]


def test_create_and_list_annotation():
    uid = _uid()
    date = _a_date()
    r = client.post("/annotations", json={
        "user_id": uid, "symbol": "SAMPL", "date": date,
        "label": "my setup", "note": "testing",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "my setup"
    assert body["window_size"] > 0          # context window captured
    assert "indicators" in body             # indicator context captured

    # list it back
    r2 = client.get(f"/annotations/{uid}")
    assert r2.status_code == 200
    lst = r2.json()
    assert len(lst["annotations"]) == 1
    assert lst["vocabulary"]["my setup"] == 1


def test_vocabulary_counts():
    uid = _uid()
    date = _a_date()
    for label in ["bounce", "bounce", "fakeout"]:
        client.post("/annotations", json={
            "user_id": uid, "symbol": "SAMPL", "date": date, "label": label,
        })
    vocab = client.get(f"/annotations/{uid}").json()["vocabulary"]
    assert vocab["bounce"] == 2
    assert vocab["fakeout"] == 1


def test_filter_by_symbol():
    uid = _uid()
    d_sampl = client.get("/bars/SAMPL").json()["bars"][100]["date"]
    d_testc = client.get("/bars/TESTC").json()["bars"][100]["date"]
    client.post("/annotations", json={"user_id": uid, "symbol": "SAMPL", "date": d_sampl, "label": "a"})
    client.post("/annotations", json={"user_id": uid, "symbol": "TESTC", "date": d_testc, "label": "b"})
    only_sampl = client.get(f"/annotations/{uid}?symbol=SAMPL").json()["annotations"]
    assert len(only_sampl) == 1
    assert only_sampl[0]["symbol"] == "SAMPL"


def test_delete_annotation():
    uid = _uid()
    date = _a_date()
    created = client.post("/annotations", json={
        "user_id": uid, "symbol": "SAMPL", "date": date, "label": "temp",
    }).json()
    aid = created["id"]
    r = client.delete(f"/annotations/{uid}/{aid}")
    assert r.status_code == 200
    assert client.get(f"/annotations/{uid}").json()["annotations"] == []


def test_delete_scoped_to_owner():
    uid = _uid()
    other = _uid()
    date = _a_date()
    created = client.post("/annotations", json={
        "user_id": uid, "symbol": "SAMPL", "date": date, "label": "mine",
    }).json()
    # another user can't delete it
    r = client.delete(f"/annotations/{other}/{created['id']}")
    assert r.status_code == 404


def test_create_bad_date_400():
    uid = _uid()
    r = client.post("/annotations", json={
        "user_id": uid, "symbol": "SAMPL", "date": "1900-01-01", "label": "x",
    })
    assert r.status_code == 400


def test_create_bad_symbol_404():
    uid = _uid()
    r = client.post("/annotations", json={
        "user_id": uid, "symbol": "NOPE", "date": "2022-01-03", "label": "x",
    })
    assert r.status_code == 404
