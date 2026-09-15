"""Shared Groq LLM helper."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

_BACKEND_DIR = Path(__file__).resolve().parents[2]
GROQ_MODEL = "openai/gpt-oss-120b"


def require_groq_api_key() -> str:
    """Return GROQ_API_KEY or raise if missing. Never log the key."""
    load_dotenv(_BACKEND_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or not api_key.strip():
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to backend/.env before using the AI endpoint."
        )
    return api_key.strip()


def get_groq_llm(temperature: float = 0) -> ChatGroq:
    """Create a Groq chat model connection (langchain-groq)."""
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=require_groq_api_key(),
        temperature=temperature,
    )
