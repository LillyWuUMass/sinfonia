from typing import Dict

from yarl import URL

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.tier_shell.domain.app import AppType


class AppConfig(BaseSettings):
    """Manage environment variables for tier1 and tier2 applications."""
    timeout_seconds: int
    root_url: URL
    port: int
    api_path: str
    
    @field_validator('root_url', mode='before')
    def _convert_to_url(cls, v):
        return URL(v)
    
    def __repr__(self):
        r = ""
        for k, v in self.model_dump().items():
            r += f" * {k}: {v}\n"
            
        return r[:-1]


class Config(BaseSettings):
    """Manage environment variables for tier shell application."""
    logging: Dict
    tier1: AppConfig
    tier2: AppConfig
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='',
        case_sensitive=False,
        frozen=True,
        )
    
    def get_app_config(self, app: AppType) -> AppConfig:
        match app:
            case AppType.Tier1:
                return self.tier1
            case AppType.Tier2:
                return self.tier2
            case _:
                raise ValueError('application not configured')
    
    def __repr__(self):        
        return f"Tier 1:\n{repr(self.tier1)}\n\nTier 2:\n{repr(self.tier2)}"
    