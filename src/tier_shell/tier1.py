import requests
from http import HTTPStatus

import typer

from src.tier_shell import strfmt
from src.tier_shell.common import (
    app_id_option, 
    uuid_option
)
from src.tier_shell.config import ApiConfig
from src.tier_shell.logger import get_api_logger


# Configure runtime environment
log = get_api_logger('tier1')
conf = ApiConfig('tier1.env')
cli = typer.Typer()


@cli.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""    
    u = conf.api_root_url / 'cloudlets'
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=conf.timeout_seconds)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, strfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Returning list of known cloudlets')
    else:
        log.info(f'{fmtsc}: Unable to get list of known cloudlets')
        exit(0)
        
    log.info(strfmt.json(resp.json()))
    
    
@cli.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()
    
    
@cli.command()
def get_deployment_recipe(uuid: str = uuid_option):
    """Retrieve information on deployment recipes."""
    u = conf.api_root_url / 'recipes' / uuid
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=conf.timeout_seconds)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)
        
    sc, fmtsc = resp.status_code, strfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Returning list of known cloudlets')
    elif sc == HTTPStatus.FORBIDDEN:
        log.info(f'{fmtsc}: Deployment recipe not accessible')
    elif sc == HTTPStatus.NOT_FOUND:
        log.info(f'{fmtsc}: Deployment recipe not found')
    else:
        print(f'{fmtsc}')
        
    log.info(strfmt.json(resp.json()))


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 1 cloudlet."""
    u = conf.api_root_url / 'deploy' / uuid / app_id
    log.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=conf.api_root_url)
    except TimeoutError:
        log.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        log.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, strfmt.http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        log.info(f'{fmtsc}: Successfully deployed to cloudlet')
    elif sc == HTTPStatus.NOT_FOUND:
        log.info(f'{fmtsc}: Failed to create deployment')
    else:
        log.info(f'{fmtsc}')
        
    log.info(strfmt.json(resp.json()))


if __name__ == "__main__":
    cli()
    