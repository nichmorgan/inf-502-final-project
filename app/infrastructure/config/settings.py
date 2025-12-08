from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

__all__ = ["Settings"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[3] / ".env", env_file_encoding="utf-8"
    )

    GITHUB_TOKEN: str
