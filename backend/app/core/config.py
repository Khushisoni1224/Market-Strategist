"""Application settings, loaded from environment variables / a local .env file."""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    project_name: str = "Market-Strategist API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # Required: secrets are never hardcoded.
    database_url: str
    secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    # Development-only shortcut; shared/deployed environments use Alembic.
    auto_create_tables: bool = False

    # Strategy engine settings; mock provider is safe and works without an API key.
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_timeout_seconds: float = 20.0
    max_recommendations: int = 3
    scoring_weights_json: str = ""

    @field_validator("secret_key")
    @classmethod
    def _secret_long_enough(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Compatibility names used by the Member 4 strategy engine.
    @property
    def LLM_PROVIDER(self) -> str:
        return self.llm_provider.lower()

    @property
    def LLM_API_KEY(self) -> str:
        return self.llm_api_key

    @property
    def LLM_MODEL(self) -> str:
        return self.llm_model

    @property
    def LLM_BASE_URL(self) -> str:
        return self.llm_base_url

    @property
    def LLM_TIMEOUT_SECONDS(self) -> float:
        return self.llm_timeout_seconds

    @property
    def MAX_RECOMMENDATIONS(self) -> int:
        return self.max_recommendations

    @property
    def SCORING_WEIGHTS_JSON(self) -> str:
        return self.scoring_weights_json


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
