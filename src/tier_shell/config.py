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


class BaseConfig(ABC):
    """Base configuration class."""
    _ENV_VARS: Dict[str, _AttributeData] = {}
    
    def __init__(self):
        self._attrs: Dict[str, Any] = {}
        
        # Set default private attributes
        for attr, data in self._ENV_VARS.items():
            self._attrs[attr] = data.default_value
    
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
                self._attrs[attr] = data.typecast(os.getenv(attr))


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
        self._attrs['API_ROOT_URL'] = URL(self._attrs['BASE_URL'] / self._attrs['API_PATH'])

        # If no scheme was provided then set default to http
        if not self._attrs['API_ROOT_URL'].scheme:
            self._attrs['API_ROOT_URL'] = URL('http://' + str(self._attrs['API_ROOT_URL']))

        # If port was provided then append to URL
        if self._attrs['PORT']:
            self._attrs['API_ROOT_URL'] = URL(self._attrs['API_ROOT_URL']).with_port(self._attrs['PORT'])
            
        return self
    
    @property
    def port(self):
        return self._attrs['PORT']
    
    @property
    def timeout_seconds(self):
        return self._attrs['TIMEOUT_SECONDS']
    
    @property
    def base_url(self):
        return self._attrs['BASE_URL']
    
    @property
    def api_path(self):
        return self._attrs['API_PATH']
    
    @property
    def api_root_url(self):
        return self._attrs['API_ROOT_URL']
    
    
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
    