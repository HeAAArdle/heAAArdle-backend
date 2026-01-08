from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    env: str = "development"

    # Optional[T] to satisfy type checker if variable is missing
    database_url: Optional[str] = None

    direct_url: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()