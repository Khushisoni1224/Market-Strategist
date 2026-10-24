"""TEMPORARY standalone settings.

Member 2 owns the real app/core/config.py. Do NOT commit this file in your PR.
Your code only needs these names to exist on `settings`.
"""
import os


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return float(default)


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return int(default)


class Settings:
    def __init__(self) -> None:
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./member4_dev.db")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", "")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.LLM_TIMEOUT_SECONDS = _get_float("LLM_TIMEOUT_SECONDS", 20)
        self.MAX_RECOMMENDATIONS = _get_int("MAX_RECOMMENDATIONS", 3)
        self.SCORING_WEIGHTS_JSON = os.getenv("SCORING_WEIGHTS_JSON", "")


settings = Settings()
