import uuid
from pathlib import Path

import typer

from src.lib.http import HTTPMethod, HTTPStatus

from dependency_injector.wiring import Provide, inject

from src.tier_shell.domain.config import AppConfig
from src.tier_shell.domain.di import AppDI

from src.tier_shell.view.common import (
    uuid_option,
    app_id_option,
    )

import src.tier_shell.service as svc

from src.domain.logger import get_default_logger


app = typer.Typer(
    name="tier2",
    help="Interactions with Tier 2 instances.",
    )

logger = get_default_logger()

_NAME_TABLE = {
    "helloworld": "00000000-0000-0000-0000-000000000000",
    "loadtest": "00000000-0000-0000-0000-000000000111",
    "openrtist-cpu": "737b5001-d27a-413f-9806-abf9bfce6746",
    "openrtist-gpu": "755e5883-0788-44da-8778-2113eddf4271",
    }


# Views

@app.command()
def deploy_app(
        uuid: str = uuid_option,
        app_id: str = app_id_option,
):
    """Deploy application to Tier 2 cloudlet.
    
    Note:
        See 'RECIPES' folder for recipe UUIDs and recipe definitions.
    """    
    if not svc.types.is_valid_uuid(uuid):
        uuid = _NAME_TABLE.get(uuid)
    
    _deploy_app(uuid, app_id)
    
    
@app.command()
def delete_app(
        uuid: str = uuid_option,
        app_id: str = app_id_option,
):
    """Delete application from Tier 2 cloudlet.
    
    Note:
        See 'RECIPES' folder for recipe UUIDs and recipe definitions.
    """
    if not svc.types.is_valid_uuid(uuid):
        uuid = _NAME_TABLE.get(uuid)
    
    _delete_app(uuid, app_id)
    
    
@app.command()
def get_carbon():
    """Get carbon level at Tier 2 cloudlet."""
    _get_carbon()


# Connectors


@inject
def _deploy_app(
        uuid: str,
        app_id: str,
        config: AppConfig = Provide[AppDI.config_tier2]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.POST,
        api_path=Path('deploy') / uuid / app_id,
        msg_by_status_code={
            HTTPStatus.OK: "Application deployed to cloudlet.",
            HTTPStatus.NOT_FOUND: "Failed to deploy application.",
            }
        )


@inject
def _delete_app(
        uuid: str,
        app_id: str,
        config: AppConfig = Provide[AppDI.config_tier2]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.DELETE,
        api_path=Path('deploy') / uuid / app_id,
        msg_by_status_code={
            HTTPStatus.NO_CONTENT: "Application deleted from cloudlet.",
            HTTPStatus.NOT_FOUND: "Failed to delete application.",
            }
        )


@inject
def _get_carbon(
        config: AppConfig = Provide[AppDI.config_tier2]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.GET,
        api_path=Path('carbon'),
        msg_by_status_code={
            HTTPStatus.OK: "Retrieved carbon data.",
            }
        )

