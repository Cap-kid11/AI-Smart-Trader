"""Auth dependencies for the API.

`get_current_user` extracts and validates the Bearer token, returning the
caller's user_id. Routes that need a logged-in user depend on it. There's also
an optional variant for endpoints that work with or without auth.
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from engine.auth import decode_token


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    """Require a valid token; return the user_id or raise 401."""
    token = _extract_token(authorization)
    user_id = decode_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


def get_optional_user(authorization: str | None = Header(default=None)) -> str | None:
    """Return the user_id if a valid token is present, else None (no error)."""
    token = _extract_token(authorization)
    return decode_token(token) if token else None
