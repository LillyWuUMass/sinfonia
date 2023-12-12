import os
import requests
from http import HTTPStatus


from dotenv import load_dotenv
import typer
import logging

from api_scripts.common import (
    app_id_option, 
    uuid_option
)
import api_scripts.strfmt as sfmt
from api_scripts.logger import get_stdout_logger
from api_scripts.url_builder import URLBuilder


PORT = None
TIMEOUT_SECONDS = None
BASE_HOSTNAME = None
API_PATH = None
API_URL = None


lg: logging.Logger = None
cli = typer.Typer()


def config_runtime_env():
    # Environment variables
    global PORT, TIMEOUT_SECONDS, BASE_HOSTNAME, API_PATH, API_URL    
    load_dotenv('./.env')
    PORT = os.getenv('TIER1_PORT', 5000)
    TIMEOUT_SECONDS = os.getenv('TIER1_API_TIMEOUT_SECONDS', 5)
    BASE_HOSTNAME = os.getenv('TIER1_BASE_HOSTNAME', 'http://localhost')
    API_PATH = os.getenv('TIER1_API_PATH', 'api/v1')
    API_URL = URLBuilder(BASE_HOSTNAME).set_port(PORT).add_path(API_PATH).build()
    
    # Formatted logger
    global lg
    lg = get_stdout_logger('tier2')


@cli.command()
def deploy_recipe():
    """Deploy recipe to cloudlet."""
    pass


if __name__ == '__main__':
    config_runtime_env()
    cli()
