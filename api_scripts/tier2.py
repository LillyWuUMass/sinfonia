import os
import requests
from http import HTTPStatus

import typer
import logging
from dotenv import load_dotenv

from api_scripts.common import (
    app_id_option, 
    uuid_option
)
import api_scripts.strfmt as sfmt
from api_scripts.logger import get_api_logger
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
    load_dotenv()
    PORT = os.getenv('TIER2_PORT', 80)
    TIMEOUT_SECONDS = int(os.getenv('TIER2_API_TIMEOUT_SECONDS', 5))
    BASE_HOSTNAME = os.getenv('TIER2_BASE_HOSTNAME', 'http://localhost')
    API_PATH = os.getenv('TIER2_API_PATH', 'api/v1')
    API_URL = URLBuilder(BASE_HOSTNAME).set_port(PORT).add_path(API_PATH).build()
    
    # Formatted logger
    global lg
    lg = get_api_logger('tier2')


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 2 cloudlet.
    
    NOTE:
    See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = URLBuilder(API_URL).add_path('deploy').add_path(uuid).add_path(app_id).build()
    lg.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        lg.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        lg.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, sfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        lg.info(f'{fmtsc}: Successfully deployed to cloudlet')
    elif sc == HTTPStatus.NOT_FOUND:
        lg.info(f'{fmtsc}: Failed to create deployment')
    else:
        lg.info(f'{fmtsc}')
        
    lg.info('\n' + sfmt.json(resp.json()))
  
  
@cli.command()
def get_candidate_cloudlets_for_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Get candidate cloudlets for recipe.
    
    NOTE:
    See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = URLBuilder(API_URL).add_path('deploy').add_path(uuid).add_path(app_id).build()
    lg.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        lg.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        lg.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, sfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        lg.info(f'{fmtsc}: Returning candidate cloudlets')
    elif sc == HTTPStatus.NOT_FOUND:
        lg.info(f'{fmtsc}: No suitable cloudlets found')
    else:
        lg.info(f'{fmtsc}')
        
    lg.info('\n' + sfmt.json(resp.json()))
  
  
if __name__ == '__main__':
    config_runtime_env()
    cli()
