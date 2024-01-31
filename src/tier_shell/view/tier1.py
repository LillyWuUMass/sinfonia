import logging

import typer

import src.tier_shell.service.api as svc_api
from src.lib.http import HTTPMethod, HTTPStatus
from src.domain.logger import get_default_logger
from src.tier_shell.domain.config import Config


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier1 instances.",
    )


logger = get_default_logger()


@app.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    svc_api.log_api_request(
        method=HTTPMethod.GET,
        api_path='cloudlets',
        msg_by_status_code={
            HTTPStatus.OK: 'Returning list of known cloudlets'
            }
        )


@app.command()
def c2():
    """c2"""    
    print('world')
