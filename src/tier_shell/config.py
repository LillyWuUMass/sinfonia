from typing import Optional

import os

from dotenv import load_dotenv
from pathlib import Path
from yarl import URL


class ApiConfig:
    """Manage API service environment variables"""
    def __init__(self, path: Optional[str | Path] = None):
        if path is None:
            load_dotenv()
        elif not os.path.isabs(path):
            path = Path(__file__).parent.resolve() / Path(path)
            load_dotenv(path)
        else:
            load_dotenv(path)
            
        self._PORT: int = int(os.getenv('PORT', default=-1))
        self._TIMEOUT_SECONDS: float = float(os.getenv('TIMEOUT_SECONDS', default=8))
        self._BASE_URL: URL = URL(os.getenv('BASE_URL', default='http://localhost'))
        self._API_PATH: str = os.getenv('API_PATH', default='')
        self._API_ROOT_URL = self._BASE_URL / self._API_PATH
        
        # Normalize service URL
        # If port was provided then append to URL
        # If no scheme was provided then set default to http
        if self._PORT != -1:
            self._API_ROOT_URL = self._API_ROOT_URL.with_port(self._PORT)
        
        if not self._API_ROOT_URL.scheme:
            self._API_ROOT_URL = self._API_ROOT_URL.with_scheme("http")
    
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
    