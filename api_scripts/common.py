from typing import Dict
from urllib.parse import urlencode, urlparse

import typer


class URLBuilder:
    """Helper class for URL manipulation"""
    def __init__(self, base_url):
        u = urlparse(base_url, scheme='http')
        self.scheme = u.scheme
        self.netloc = u.netloc
        self.path = u.path
        self.query = {} if u.query == '' else u.query

    def add_path(self, path: str):
        self.path = f'{self.path}/{path}'
        return self  # For daisy chaining

    def add_query_param(self, key, value):
        if key in self.query:
            raise AttributeError(f"parameter \'{key}\' already exists")
                
        self.query[key] = value
        return self  # For daisy chaining

    def build(self) -> str:
        query = urlencode(self.query) if type(self.query) == dict else self.query
        u = f'{self.scheme}://{self.netloc}{self.path}'
        if query != '':
            u = f'{u}?{query}'
        return u


port_option = typer.Option(5000, help='Application port.')
uuid_option = typer.Option('00000000-0000-0000-0000-000000000000', help='UUID for recipe. See \'RECIPES\' folder for recipe definitions')
