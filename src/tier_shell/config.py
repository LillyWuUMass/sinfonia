from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import os

from dotenv import load_dotenv
from pathlib import Path
from yarl import URL


@dataclass(init=True)
class _AttributeData:
    default_value: Any
    typecast: Callable[[Any], Any] = str


def _private_attr_name(name: str) -> str:
    return '_' + name


class BaseConfig(ABC):
    _ENV_VARS: Dict[str, _AttributeData] = {}
    
    def __init__(self):
        # Set default private attributes
        for attr, data in self._ENV_VARS.items():
            setattr(self, _private_attr_name(attr), data.default_value)
    
    @abstractmethod
    def from_env(self, path: str | URL):
        if path is None:
            load_dotenv()
        else:
            load_dotenv(path)
            
        for attr, data in self._ENV_VARS.items():
            if attr in os.environ:
                setattr(
                    self, 
                    _private_attr_name(attr), 
                    data.typecast(os.getenv(attr))
                    )


class ApiConfig(BaseConfig):
    """Manage API service environment variables."""
    
    _ENV_VARS = {
        'PORT': _AttributeData(
            default_value=None, 
            typecast=int
            ),
        'TIMEOUT_SECONDS': _AttributeData(
            default_value=float('inf'), 
            typecast=float
            ),
        'BASE_URL': _AttributeData(
            default_value=URL('http://localhost'), 
            typecast=URL
            ),
        'API_PATH': _AttributeData(
            default_value='',
            typecast=str
            ),
    }
    
    def __init__(self):
        super().__init__()
        
    def from_env(self, path: str | URL) -> ApiConfig:
        super().from_env(path)
    
        # Construct API root URL
        self._API_ROOT_URL = self._BASE_URL / self._API_PATH

        # If port was provided then append to URL
        if self._PORT != -1:
            self._API_ROOT_URL = self._API_ROOT_URL.with_port(self._PORT)
        
        # If no scheme was provided then set default to http
        if not self._API_ROOT_URL.scheme:
            self._API_ROOT_URL = self._API_ROOT_URL.with_scheme("http")
            
        return self
    
    @property
    def port(self):
        return self._PORT
    
    @property
    def timeout_seconds(self):
        return self._TIMEOUT_SECONDS
    
    @property
    def base_url(self):
        return self._BASE_URL
    
    @property
    def api_path(self):
        return self._API_PATH
    
    @property
    def api_root_url(self):
        return self._API_ROOT_URL
    
    
class AppConfig(BaseConfig):
    def __init__(self):
        self._api = ApiConfig()
        
    def from_env(self, path: str | URL) -> AppConfig:
        self._api = self._api.from_env(path)
        return self
        
    @property
    def api(self):
        return self._api
    