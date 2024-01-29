from pathlib import Path

from yarl import URL

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreConfig(BaseSettings):
    """Manage environment variables for tier shell application."""
    timeout_seconds: int
    root_url: URL
    port: int
    api_path: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='',
        case_sensitive=False,
        frozen=True,
        )

    @field_validator('root_url', mode='before')
    def _convert_to_url(cls, v):
        return URL(v)
    