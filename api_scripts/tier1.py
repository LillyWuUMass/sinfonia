from typing import Optional
from urllib.parse import urlencode

import requests
import typer

from api_scripts.common import URLBuilder, uuid_option, port_option


BASE_URL = 'http://localhost/api/v1'


cli = typer.Typer()


@cli.command()
def get_known_cloudlets(
        port: Optional[int] = port_option,
):
    u = URLBuilder(BASE_URL).add_path('cloudlets').build()
    
    
@cli.command()
def hello():
    print("hello")
    


if __name__ == "__main__":
    cli()