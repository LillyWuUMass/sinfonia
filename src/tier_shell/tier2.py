import requests
from http import HTTPStatus

import typer

import src.lib.http.format as httpfmt
from src.tier_shell.common import (
    app_id_option, 
    uuid_option
)
from src.tier_shell.domain_legacy.app.context import TierShellContext
from src.domain.logger import get_default_logger


# Configure runtime environment
logger = get_default_logger()
conf = TierShellContext(_env_file='./src/tier_shell/tier2.api.env')
cli = typer.Typer()


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 2 cloudlet.
    
    Note:
        See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = conf.root_url / 'deploy' / uuid / app_id
    logger.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=conf.timeout_seconds)
    except requests.Timeout:
        logger.critical(f'api timeout exceeded ({conf.timeout_seconds} seconds)')
        exit(0)
    except Exception as e:
        logger.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, httpfmt.http_repr(resp.status_code)
    if sc == HTTPStatus.OK:
        logger.info(f'{fmtsc}: Successfully deployed to cloudlet')
    elif sc == HTTPStatus.NOT_FOUND:
        logger.info(f'{fmtsc}: Failed to create deployment')
    else:
        logger.info(f'{fmtsc}')
        
    try:
        logger.info(httpfmt.http_repr(resp.json()))
    except:
        pass
  
  
@cli.command()
def get_candidate_cloudlets(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Get candidate cloudlets for recipe.
    
    Note:
        See 'RECIPES' folder for recipe UUIDS and recipe definitions.
    """
    u = conf.root_url / 'deploy' / uuid / app_id
    logger.info(f'Sending GET request to {u}')
    
    try:
        resp = requests.get(u, timeout=conf.timeout_seconds)
    except TimeoutError:
        logger.critical('api timeout exceeded')
        exit(0)
    except Exception as e:
        logger.critical(f'unable to send request: {str(e)}')
        exit(0)

    sc, fmtsc = resp.status_code, httpfmt.http_repr(resp.status_code)
    if sc == HTTPStatus.OK:
        logger.info(f'{fmtsc}: Returning candidate cloudlets')
    elif sc == HTTPStatus.NOT_FOUND:
        logger.info(f'{fmtsc}: No suitable cloudlets found')
    else:
        logger.info(f'{fmtsc}')
        
    try:
        logger.info(httpfmt.http_repr(resp.json()))
    except:
        pass
  
  
if __name__ == '__main__':
    cli()
