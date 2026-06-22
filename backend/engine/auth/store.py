"""Authentication — real user accounts.

JWT-based auth with bcrypt password hashing, self-contained on the backend (no
third-party auth service needed). This replaces the hardcoded "demo-user" so
each person's portfolio, annotations, and vocabulary are truly theirs.

Security notes:
- Passwords are bcrypt-hashed; plaintext is never stored.
- Tokens are signed with a secret from the JWT_SECRET env var. A dev default is
  used if unset, with a loud warning — set a real secret in production.
- This handles login only. It never touches payment info or other sensitive
  credentials.
"""
from __future__ import annotations

import os
import secrets
import warnings
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlmodel import Field, Session, SQLModel, select

from engine.db import engine as _engine

# --- Config ---

_DEV_SECRET = "dev-only-insecure-secret-change-me"
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    warnings.warn(
        "JWT_SECRET not set — using an insecure development secret. "
        "Set JWT_SECRET in the environment before deploying.",
        stacklevel=2,
    )
    JWT_SECRET = _DEV_SECRET

JWT_ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 24 * 7  # one week


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # public, stable identifier used everywhere else (portfolios, annotations)
    user_id: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def init_db() -> None:
    SQLModel.metadata.create_all(_engine)


init_db()


# --- Password hashing ---

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# --- Tokens ---

def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=TOKEN_TTL_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    """Return the user_id from a valid token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


# --- Account operations ---

class AuthError(Exception):
    """Raised for signup/login failures."""


def _session() -> Session:
    return Session(_engine)


def signup(email: str, password: str) -> tuple[User, str]:
    """Create an account. Returns (user, token). Raises AuthError if taken."""
    email = email.strip().lower()
    if not email or "@" not in email:
        raise AuthError("a valid email is required")
    if len(password) < 8:
        raise AuthError("password must be at least 8 characters")

    with _session() as s:
        existing = s.exec(select(User).where(User.email == email)).first()
        if existing:
            raise AuthError("an account with that email already exists")

        user_id = "u_" + secrets.token_hex(8)
        user = User(
            user_id=user_id,
            email=email,
            password_hash=hash_password(password),
        )
        s.add(user)
        s.commit()
        s.refresh(user)
        return user, create_token(user.user_id)


def login(email: str, password: str) -> tuple[User, str]:
    """Authenticate. Returns (user, token). Raises AuthError on bad creds."""
    email = email.strip().lower()
    with _session() as s:
        user = s.exec(select(User).where(User.email == email)).first()
        # Always run a verify to reduce timing differences, even if user missing.
        ok = verify_password(password, user.password_hash) if user else verify_password(password, hash_password("x"))
        if not user or not ok:
            raise AuthError("invalid email or password")
        return user, create_token(user.user_id)


def get_user(user_id: str) -> User | None:
    with _session() as s:
        return s.exec(select(User).where(User.user_id == user_id)).first()
