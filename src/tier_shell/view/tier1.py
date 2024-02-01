from pathlib import Path

import typer

from src.lib.http import HTTPMethod, HTTPStatus

from dependency_injector.wiring import Provide, inject

from src.tier_shell.domain.config import AppConfig
from src.tier_shell.domain.di import AppDI

import src.tier_shell.service as svc

from src.tier_shell.view.common import uuid_option


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier 1 instances.",
    )


# Views

@app.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    _get_known_cloudlets()


@app.command()
def get_deployment_recipe(uuid: str = uuid_option):
    """Retrieve information on deployment recipes."""
    _get_deployment_recipe(uuid)


# Connectors

@inject
def _get_known_cloudlets(
        config: AppConfig = Provide[AppDI.config_tier1]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.GET,
        api_path='cloudlets',
        msg_by_status_code={
            HTTPStatus.OK: 'Returning list of known cloudlets'
            }
        )
    
    
@inject
def _get_deployment_recipe(
        uuid: str,
        config: AppConfig = Provide[AppDI.config_tier1],
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.GET,
        api_path=Path('recipes') / uuid,
        msg_by_status_code={
            HTTPStatus.OK: 'Returning list of known cloudlets.',
            HTTPStatus.FORBIDDEN: 'Cannot access deployment recipe.',
            HTTPStatus.NOT_FOUND: 'Deployment recipe not found.',
            }
        )
