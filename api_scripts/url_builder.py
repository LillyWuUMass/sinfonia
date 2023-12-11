from urllib.parse import urlencode, urlparse


class URLBuilder:
    """Helper class for URL manipulation"""
    def __init__(self, base_url):
        u = urlparse(base_url, scheme='http')
        self.scheme = u.scheme
        self.hostname = u.hostname
        self.port = u.port
        self.path = u.path
        self.query = {} if u.query == '' else u.query

    def set_port(self, port: int):
        self.port = port
        return self  # For daisy chaining

    def add_path(self, path: str):
        self.path = f'{self.path}/{path}'
        return self  # For daisy chaining

    def add_query_param(self, key, value):
        if key in self.query:
            raise AttributeError(f"parameter \'{key}\' already exists")
                
        self.query[key] = value
        return self  # For daisy chaining

    def build(self) -> str:        
        # Base url
        u = f'{self.scheme}://{self.hostname}'
        
        # Port number
        if self.port != None:
            u = f'{u}:{self.port}'
            
        # Path
        u = f'{u}{self.path}'
         
        # Query parameters
        query = urlencode(self.query) if type(self.query) == dict else self.query
        if query != '':
            u = f'{u}?{query}'
            
        return u
