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

    # Required: no defaults, so secrets are never hardcoded.
    database_url: str
    secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Comma-separated string (simpler to write in .env than JSON).
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # DEVELOPMENT ONLY. Shared/deployed environments must use Alembic.
    auto_create_tables: bool = False

    @field_validator("secret_key")
    @classmethod
    def _secret_long_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
