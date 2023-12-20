import os
import requests
from http import HTTPStatus

import typer
import logging
from dotenv import load_dotenv
from yarl import URL

from api_scripts.common import (
    app_id_option, 
    uuid_option
)
import api_scripts.strfmt as sf
from api_scripts.logger import get_api_logger


PORT = None
TIMEOUT_SECONDS = None
BASE_HOSTNAME = None
API_PATH = None
API_URL = None


log = get_api_logger('tier1')
cli = typer.Typer()


def config_runtime_env():
    # Environment variables
    global PORT, TIMEOUT_SECONDS, BASE_HOSTNAME, API_PATH, API_URL    
    load_dotenv()
    PORT = int(os.getenv('TIER1_PORT', 5000))
    TIMEOUT_SECONDS = int(os.getenv('TIER1_API_TIMEOUT_SECONDS', 5))
    BASE_HOSTNAME = os.getenv('TIER1_BASE_HOSTNAME', 'http://localhost')
    API_PATH = os.getenv('TIER1_API_PATH', 'api/v1')
    API_URL = URL(BASE_HOSTNAME).with_port(PORT).with_path(API_PATH)


@cli.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    u = API_URL / 'cloudlets'
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, sf.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Returning list of known cloudlets')
    else:
        log.info(f'{fmtsc}: Unable to get list of known cloudlets')
        
    log.info('\n' + sf.json(resp.json()))
    
    
    
@cli.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()
    
    
@cli.command(help='Retrieve information on deployment recipes.')
def get_deployment_recipe(uuid: str = uuid_option):
    u = API_URL / 'recipes' / uuid
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, sf.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Returning list of known cloudlets')
    elif sc == HTTPStatus.FORBIDDEN:
        log.info(f'{fmtsc}: Deployment recipe not accessible')
    elif sc == HTTPStatus.NOT_FOUND:
        log.info(f'{fmtsc}: Deployment recipe not found')
    else:
        print(f'{fmtsc}')
        
    log.info('\n' + sf.json(resp.json()))


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 1 cloudlet."""
    u = API_URL / 'deploy' / uuid / app_id
    log.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=TIMEOUT_SECONDS)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, sf.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Successfully deployed to cloudlet')
    elif sc == HTTPStatus.NOT_FOUND:
        log.info(f'{fmtsc}: Failed to create deployment')
    else:
        log.info(f'{fmtsc}')
        
    log.info('\n' + sf.json(resp.json()))


if __name__ == "__main__":
    config_runtime_env()
    cli()
    