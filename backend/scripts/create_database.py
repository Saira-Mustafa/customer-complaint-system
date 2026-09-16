"""One-time helper: create the customer_complaints database if missing.

Does not create tables — Alembic migrations handle schema.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

PG_BIN = Path(r"C:\Program Files\PostgreSQL\18\bin")


def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL is missing from backend/.env")
        return 1

    match = re.match(
        r"postgresql\+psycopg://([^:]+):([^@]+)@([^:/]+):(\d+)/([^?\s]+)",
        url,
    )
    if not match:
        print("DATABASE_URL format not recognized")
        return 1

    user, password, host, port, db_name = match.groups()
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    if PG_BIN.exists():
        env["PATH"] = str(PG_BIN) + os.pathsep + env.get("PATH", "")

    psql = str(PG_BIN / "psql.exe") if (PG_BIN / "psql.exe").exists() else "psql"

    check = subprocess.run(
        [
            psql,
            "-U",
            user,
            "-h",
            host,
            "-p",
            port,
            "-d",
            "postgres",
            "-tAc",
            f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if check.returncode != 0:
        print("Failed to query PostgreSQL:")
        print(check.stderr.strip()[:300])
        return 1

    if check.stdout.strip() == "1":
        print(f"Database already exists: {db_name}")
        return 0

    create = subprocess.run(
        [
            psql,
            "-U",
            user,
            "-h",
            host,
            "-p",
            port,
            "-d",
            "postgres",
            "-c",
            f'CREATE DATABASE "{db_name}"',
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if create.returncode != 0:
        print("Failed to create database:")
        print(create.stderr.strip()[:300])
        return 1

    print(f"Created database: {db_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
