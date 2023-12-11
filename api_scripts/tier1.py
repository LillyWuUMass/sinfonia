from typing import Optional

import pprint
import requests
import typer
from urllib.parse import urlencode

from api_scripts.common import URLBuilder, uuid_option, port_option


PORT = 5000
BASE_URL = 'http://localhost'
API_PATH = 'api/v1'
TIMEOUT_SECONDS = 5  # Seconds


pp = pprint.PrettyPrinter(indent=4)


cli = typer.Typer()


@cli.command()
def get_known_cloudlets(
        port: Optional[int] = port_option,
):
    u = URLBuilder(BASE_URL).set_port(PORT).add_path(API_PATH).add_path('cloudlets')
    print(u.build())
    resp = requests.get(u.build(), timeout=TIMEOUT_SECONDS)
    try:
        pp.pprint(resp.json())
    except Exception as e:
        print('empty api response: remember to start tier1 server')
    
    
@cli.command()
def hello():
    print("hello")
    


if __name__ == "__main__":
    cli()