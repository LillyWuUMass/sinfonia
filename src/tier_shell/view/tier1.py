from pathlib import Path

import typer

from src.lib.http import HTTPMethod, HTTPStatus

from dependency_injector.wiring import Provide, inject

from src.tier_shell.domain.config import AppConfig
from src.tier_shell.domain.di import AppDI

from src.tier_shell.view.common import (
    uuid_option,
    app_id_option,
    lookup_uuid,
    )

import src.tier_shell.service as svc


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
def get_deploy_app(uuid: str = uuid_option):
    """Retrieve information on deployment app."""
    _get_deploy_app(uuid)
    
    
@app.command()
def deploy_app(
        uuid: str = uuid_option,
        app_id: str = app_id_option,
):
    """Retrieve information on deployment recipes."""
    if not svc.types.is_valid_uuid(uuid):
        uuid = lookup_uuid(uuid)
    
    _deploy_app(uuid, app_id)


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
def _get_deploy_app(
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
    
    
@inject
def _deploy_app(
        uuid: str,
        app_id: str,
        config: AppConfig = Provide[AppDI.config_tier1]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.POST,
        api_path=Path('deploy') / uuid / app_id,
        msg_by_status_code={
            HTTPStatus.OK: 'App deployed.'
            }
        )
