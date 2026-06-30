from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, sourced from the environment.

    SQLite is an acceptable local fallback; Postgres is the primary store.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://compliance:compliance@localhost:5432/compliance"
    app_env: str = "development"

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "obligation-documents"
    signed_url_expiry_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
