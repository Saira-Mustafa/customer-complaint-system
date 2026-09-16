"""SQLAlchemy engine and session helpers."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _ensure_libpq_on_path() -> None:
    """On Windows, prefer the installed PostgreSQL libpq when psycopg binary is blocked."""
    candidates = [
        Path(r"C:\Program Files\PostgreSQL\18\bin"),
        Path(r"C:\Program Files\PostgreSQL\17\bin"),
        Path(r"C:\Program Files\PostgreSQL\16\bin"),
    ]
    current = os.environ.get("PATH", "")
    for candidate in candidates:
        if candidate.exists() and str(candidate) not in current:
            os.environ["PATH"] = str(candidate) + os.pathsep + current
            break


_ensure_libpq_on_path()

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
