from http import HTTPStatus

import requests
import typer

from api_scripts.common import (
    app_id_option, 
    uuid_option
)
import api_scripts.style_printer as sp
from api_scripts.url_builder import URLBuilder


PORT = 5000
TIMEOUT_SECONDS = 5  # Seconds
BASE_URL = 'http://localhost'
API_PATH = 'api/v1'
API_URL = URLBuilder(BASE_URL).set_port(PORT).add_path(API_PATH).build()


cli = typer.Typer()


def strfmt_http_status_code(code: int) -> str:
    if code >= 200 and code <= 299:
        return sp.bold(sp.green(str(code)))
    elif code >= 400 and code <= 599:
        return sp.bold(sp.red(str(code)))
    return sp.bold(sp.yellow(str(code)))


@cli.command(help='Return manifest of known Tier 2 cloudlets.')
def get_known_cloudlets():
    u = URLBuilder(API_URL).add_path('cloudlets').build()
    print('Sending request to', u)
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        print(sp.red('api timeout exceeded'))
        exit(0)
    except Exception as e:
        print(sp.red('unable to send request:', str(e)))
        exit(0)
        
    sc, fmtsc = resp.status_code, strfmt_http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        print(f'{fmtsc}:', 'Returning list of known cloudlets')
        print(sp.json(resp.json()))
    else:
        print(f'{fmtsc}:', 'Unable to get list of known cloudlets')
    
    
    
@cli.command(help='Update cloudlet resource metrics.')
def update_cloudlet_resource_metrics():
    raise NotImplementedError()
    
    
@cli.command(help='Retrieve information on deployment recipes.')
def get_deployment_recipe(uuid: str = uuid_option):
    u = URLBuilder(API_URL).add_path('recipes').add_path(uuid).build()
    print('Sending request to', u)
    
    try:
        resp = requests.get(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        print(sp.red('api timeout exceeded'))
        exit(0)
    except Exception as e:
        print(sp.red('unable to send request:', str(e)))
        exit(0)
        
    sc, fmtsc = resp.status_code, strfmt_http_status_code(resp.status_code)
    if sc == HTTPStatus.OK:
        print(f'{fmtsc}:', 'Returning list of known cloudlets')
        print(sp.json(resp.json()))
    elif sc == HTTPStatus.FORBIDDEN:
        print(f'{fmtsc}:', 'Deployment recipe not accessible')
    elif sc == HTTPStatus.NOT_FOUND:
        print(f'{fmtsc}:', 'Deployment recipe not found')


@cli.command(help='Deploy a recipe.')
def deploy_recipe(
    uuid: str = uuid_option, 
    app_id: str = app_id_option,
):
    u = URLBuilder(API_URL).add_path(uuid).add_path(app_id).build()
    print('Sending request to', u)
    
    try:
        resp = requests.post(u, timeout=TIMEOUT_SECONDS)
    except ConnectionError:
        print(sp.red('api timeout exceeded'))
        exit(0)
    except Exception as e:
        print(sp.red('unable to send request:', str(e)))
        exit(0)

    pass


if __name__ == "__main__":
    cli()
    