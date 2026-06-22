"""Tests for authentication and protected routes.

Run from backend/:  python -m pytest tests/test_auth.py -q
"""
import uuid

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


def test_signup_returns_token():
    r = client.post("/auth/signup", json={"email": _email(), "password": "strongpass1"})
    assert r.status_code == 200
    body = r.json()
    assert body["token"]
    assert body["user_id"].startswith("u_")


def test_signup_weak_password_rejected():
    r = client.post("/auth/signup", json={"email": _email(), "password": "short"})
    assert r.status_code == 422  # Pydantic min_length


def test_duplicate_email_rejected():
    email = _email()
    client.post("/auth/signup", json={"email": email, "password": "strongpass1"})
    r = client.post("/auth/signup", json={"email": email, "password": "strongpass1"})
    assert r.status_code == 400


def test_login_works():
    email = _email()
    client.post("/auth/signup", json={"email": email, "password": "strongpass1"})
    r = client.post("/auth/login", json={"email": email, "password": "strongpass1"})
    assert r.status_code == 200
    assert r.json()["token"]


def test_login_wrong_password():
    email = _email()
    client.post("/auth/signup", json={"email": email, "password": "strongpass1"})
    r = client.post("/auth/login", json={"email": email, "password": "wrongpass1"})
    assert r.status_code == 401


def test_login_unknown_user():
    r = client.post("/auth/login", json={"email": _email(), "password": "whatever1"})
    assert r.status_code == 401


def test_me_requires_token():
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_token():
    email = _email()
    token = client.post("/auth/signup", json={"email": email, "password": "strongpass1"}).json()["token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == email


def test_me_bad_token():
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


def test_protected_paper_route():
    email = _email()
    token = client.post("/auth/signup", json={"email": email, "password": "strongpass1"}).json()["token"]
    # authenticated portfolio route uses the token's user
    r = client.get("/me/paper", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["cash"] == r.json()["starting_cash"]
    # without token -> 401
    assert client.get("/me/paper").status_code == 401


def test_isolation_between_users():
    # two users have independent portfolios
    t1 = client.post("/auth/signup", json={"email": _email(), "password": "strongpass1"}).json()
    t2 = client.post("/auth/signup", json={"email": _email(), "password": "strongpass1"}).json()
    client.post("/paper/buy", json={"user_id": t1["user_id"], "symbol": "SAMPL", "shares": 10})
    p2 = client.get("/me/paper", headers={"Authorization": f"Bearer {t2['token']}"}).json()
    assert p2["holdings"] == []  # user 2 unaffected
