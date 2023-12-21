import requests
from http import HTTPStatus

import typer

from api_scripts import strfmt
from api_scripts.common import (
    app_id_option, 
    uuid_option
)
from api_scripts.config import ApiConfig
from api_scripts.logger import get_api_logger


# Configure runtime environment
log = get_api_logger('tier2')
conf = ApiConfig('tier2.env')
cli = typer.Typer()


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 2 cloudlet.
    
    NOTE:
    See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = conf.api_root_url / 'deploy' / 'uuid' / 'app_id'
    log.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=conf.timeout_seconds)
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
  
  
@cli.command()
def get_candidate_cloudlets_for_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Get candidate cloudlets for recipe.
    
    NOTE:
    See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = conf.api_root_url / 'deploy' / 'uuid' / 'app_id'
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
        log.info(f'{fmtsc}: Returning candidate cloudlets')
    elif sc == HTTPStatus.NOT_FOUND:
        log.info(f'{fmtsc}: No suitable cloudlets found')
    else:
        log.info(f'{fmtsc}')
        
    log.info(strfmt.json(resp.json()))
  
  
if __name__ == '__main__':
    cli()
