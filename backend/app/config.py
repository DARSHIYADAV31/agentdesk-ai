from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV, extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    llm_timeout_seconds: int = 30
    llm_max_attempts: int = 3
    mcp_timeout_seconds: int = 20
    vector_store: str = "faiss"
    database_url: str = "sqlite:///./dev.db"
    webhook_secret: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
