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
conf = ApiConfig(_env_file='./src/tier_shell/tier1.api.env')
cli = typer.Typer()


@cli.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""    
    u = conf.API_ROOT_URL / 'cloudlets'
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=conf.TIMEOUT_SECONDS)
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
        
    try:
        log.info(strfmt.json(resp.json()))
    except:
        pass
    
    
@cli.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()
    
    
@cli.command()
def get_deployment_recipe(uuid: str = uuid_option):
    """Retrieve information on deployment recipes."""
    u = conf.API_ROOT_URL / 'recipes' / uuid
    log.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=conf.TIMEOUT_SECONDS)
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
        log.info(f'{fmtsc}')
        
    try:
        log.info(strfmt.json(resp.json()))
    except:
        pass


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 1 cloudlet."""
    u = conf.API_ROOT_URL / 'deploy' / uuid / app_id
    log.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=conf.TIMEOUT_SECONDS)
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
        
    try:
        log.info(strfmt.json(resp.json()))
    except:
        pass


if __name__ == "__main__":
    cli()
    