"""Shared database engine.

Both the annotation store and the paper-trading store use this single SQLite
engine, so there's one database file and one place to switch to Postgres later
(change DB_URL). Importing this module does not create tables — each store
calls create_all for its own models, which is idempotent.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlmodel import create_engine

# One DB for the whole app. Override with VERIDIAN_DB_URL for Postgres, etc.
_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "veridian.db"
DB_URL = os.environ.get("VERIDIAN_DB_URL", f"sqlite:///{_DEFAULT_PATH}")

# Hosting platforms (Railway/Render/Heroku) often provide a URL starting with
# "postgres://", but SQLAlchemy needs "postgresql://". Normalize it, and pin the
# psycopg (v3) driver so the dialect is unambiguous.
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# check_same_thread=False is needed for SQLite under FastAPI's threadpool.
_connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, echo=False, connect_args=_connect_args)
