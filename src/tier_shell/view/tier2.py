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


app = typer.Typer(
    name="tier2",
    help="Interactions with Tier 2 instances.",
    )


# Views

@app.command()
def deploy_recipe(
        uuid: str = uuid_option,
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 2 cloudlet.
    
    Note:
        See 'RECIPES' folder for recipe UUIDs and recipe definitions.
    """
    _deploy_recipe(uuid, app_id)
    

@app.command()
def c2():
    """c2"""    
    print('c2')


# Connectors


@inject
def _deploy_recipe(
        uuid: str,
        app_id: str,
        config: AppConfig = Provide[AppDI.config_tier2]
):
    svc.api.log_api_request(
        config=config,
        method=HTTPMethod.POST,
        api_path=Path('deploy') / uuid / app_id,
        msg_by_status_code={
            HTTPStatus.OK: "Recipe deployed to cloudlet.",
            HTTPStatus.NOT_FOUND: "Failed to create deployment.",
            }
        )
