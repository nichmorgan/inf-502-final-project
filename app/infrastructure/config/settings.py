from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[3] / ".env", env_file_encoding="utf-8"
    )

    GITHUB_TOKEN: str
    STORAGE_FOLDER: str = ".storage/"
    CACHE_TTL_SECONDS: int = 60 * 60
