from yarl import URL

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiConfig(BaseSettings):
    """API environment variables."""
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file_encoding='utf-8'
        )

    TIMEOUT_SECONDS: int
    PORT: int
    API_ROOT_URL: URL

    @field_validator('API_ROOT_URL', mode='before')
    def convert_to_url(cls, v):
        return URL(v)
