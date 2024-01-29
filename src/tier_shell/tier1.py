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
conf = TierShellContext(_env_file='src/tier_shell/tier1.api.env')
cli = typer.Typer()


@cli.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""     
    u = conf.root_url / 'cloudlets'
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
        logger.info(f'{fmtsc}: Returning list of known cloudlets')
    else:
        logger.info(f'{fmtsc}: Unable to get list of known cloudlets')
        exit(0)
        
    try:
        logger.info(httpfmt.http_repr(resp.json()))
    except:
        pass
    
    
@cli.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()
    
    
@cli.command()
def get_deployment_recipe(uuid: str = uuid_option):
    """Retrieve information on deployment recipes."""
    u = conf.root_url / 'recipes' / uuid
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
        logger.info(f'{fmtsc}: Returning list of known cloudlets')
    elif sc == HTTPStatus.FORBIDDEN:
        logger.info(f'{fmtsc}: Deployment recipe not accessible')
    elif sc == HTTPStatus.NOT_FOUND:
        logger.info(f'{fmtsc}: Deployment recipe not found')
    else:
        logger.info(f'{fmtsc}')
        
    try:
        logger.info(httpfmt.http_repr(resp.json()))
    except:
        pass


@cli.command()
def deploy_recipe(
        uuid: str = uuid_option, 
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 1 cloudlet."""
    u = conf.root_url / 'deploy' / uuid / app_id
    logger.info(f'Sending POST request to {u}')
    
    try:
        resp = requests.post(u, timeout=conf.timeout_seconds)
    except TimeoutError:
        logger.critical('api timeout exceeded')
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


if __name__ == "__main__":
    cli()
    