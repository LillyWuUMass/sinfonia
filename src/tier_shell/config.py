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
    """Contains data relating to an attribute."""
    default_value: Any
    typecast: Callable[[Any], Any] = str


def _private_attr_name(name: str) -> str:
    """Convert attribute name to a private attribute name.
    
    A private attribute name is simply the attribute name pprepended
    with an underscore ('_'). E.g. 'a' -> '_a'.
    
    Args:
        name -- str
    
    Returns:
        str: Private attribute name
    """
    return '_' + name


class BaseConfig(ABC):
    """Base configuration class."""
    _ENV_VARS: Dict[str, _AttributeData] = {}
    
    def __init__(self):
        # Set default private attributes
        for attr, data in self._ENV_VARS.items():
            setattr(self, _private_attr_name(attr), data.default_value)
    
    @abstractmethod
    def from_env(self, path: Optional[str | Path] = None):
        """Load environment variables from current environment.
        
        Args:
            path -- Optional[str | Path]: 
                Path to environment file (.env) [Defaults to './.env']
            
        Returns:
            Instance of the class.
        """
        if path is None:
            load_dotenv()
        else:
            path = os.path.abspath(path)
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
            default_value=None, 
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
        
    def from_env(self, path: Optional[str | Path] = None) -> ApiConfig:
        super().from_env(path)
    
        # Construct API root URL
        self._API_ROOT_URL = URL(self._BASE_URL / self._API_PATH)

        # If no scheme was provided then set default to http
        if not self._API_ROOT_URL.scheme:
            self._API_ROOT_URL = URL('http://' + str(self._API_ROOT_URL))

        # If port was provided then append to URL
        if self._PORT != -1:
            self._API_ROOT_URL = URL(self._API_ROOT_URL).with_port(self._PORT)
            
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
    """Applicaton configuration class.
    
    This class contains all known configuration classes. Each attribute in this 
    class represents a specific configuration usecase. It is recommended that
    this class be used when managing application-wide environment variables.
    """
    def __init__(self):
        self._configs: Dict[str, BaseConfig] = {}
        self._configs['api'] = ApiConfig()
        
    def from_env(self, path: Optional[str | Path] = None) -> AppConfig:
        for cfg in self._configs.keys():
            self._configs[cfg] = self._configs[cfg].from_env(path)
            
        return self
        
    @property
    def api(self):
        return self._configs['api']
    