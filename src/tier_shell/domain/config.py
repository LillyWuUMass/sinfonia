from typing import Dict

from yarl import URL

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import src.lib.str.format as strfmt


class AppConfig(BaseSettings):
    timeout_seconds: int
    root_url: URL
    port: int
    api_path: str
    
    @field_validator('root_url', mode='before')
    def _convert_to_url(cls, v):
        return URL(v)


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
    
    def __repr__(self):
        def repr_app_config(cfg: AppConfig):
            r = ""
            for k, v in cfg.model_dump().items():
                r += f" * {k}: {v}\n"
                
            return strfmt.white(r[:-1])
                
        
        return f"Tier 1:\n{repr_app_config(self.tier1)}\n\nTier 2:\n{repr_app_config(self.tier2)}"
    