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
    lg = get_stdout_logger('tier1')


@cli.command(help='Return manifest of known Tier 2 cloudlets.')
def get_known_cloudlets():
    u = URLBuilder(API_URL).add_path('cloudlets').build()
    lg.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        lg.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        lg.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, sfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        lg.info(f'{fmtsc}: Returning list of known cloudlets')
        lg.info(sfmt.json(resp.json()))
    else:
        lg.warn(f'{fmtsc}: Unable to get list of known cloudlets')
    
    
    
@cli.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()
    
    
@cli.command(help='Retrieve information on deployment recipes.')
def get_deployment_recipe(uuid: str = uuid_option):
    u = URLBuilder(API_URL).add_path('recipes').add_path(uuid).build()
    lg.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        lg.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        lg.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, sfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        lg.info(f'{fmtsc}: Returning list of known cloudlets')
        lg.info(sfmt.json(resp.json()))
    elif sc == HTTPStatus.FORBIDDEN:
        lg.warn(f'{fmtsc}: Deployment recipe not accessible')
    elif sc == HTTPStatus.NOT_FOUND:
        lg.warn(f'{fmtsc}: Deployment recipe not found')
    else:
        print(f'{fmtsc}:')


@cli.command()
def deploy_recipe(
    uuid: str = uuid_option, 
    app_id: str = app_id_option,
):
    """Deploy recipe to Tier 1 cloudlet.
    
    WARNING: As of now, this feature is not available for Tier 1
    """
    u = URLBuilder(API_URL).add_path('deploy').add_path(uuid).add_path(app_id).build()
    lg.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        lg.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        lg.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, sfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        lg.info(f'{fmtsc}: Successfully deployed to cloudlet')
        lg.info(sfmt.json(resp.json()))
    elif sc == HTTPStatus.NOT_FOUND:
        lg.warn(f'{fmtsc}: Failed to create deployment')
    else:
        lg.warn(f'{fmtsc}:')


if __name__ == "__main__":
    config_runtime_env()
    cli()
    