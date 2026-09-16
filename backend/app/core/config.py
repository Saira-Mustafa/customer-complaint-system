"""Application settings loaded from backend/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str | None = None
    database_url: str = (
        "postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/customer_complaints"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
