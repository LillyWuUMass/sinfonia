from pathlib import Path

import typer

from src.lib.http import HTTPMethod, HTTPStatus

from src.tier_shell.domain.app import AppType

from src.tier_shell.view.common import (
    uuid_option,
    app_id_option,
    )

import src.tier_shell.service as svc


app = typer.Typer(
    name="tier2",
    help="Interactions with Tier 2 instances.",
    )


@app.command()
def deploy_recipe(
        uuid: str = uuid_option,
        app_id: str = app_id_option,
):
    """Deploy recipe to Tier 2 cloudlet.
    
    Note:
        See 'RECIPES' folder for recipe UUIDs and recipe definitions.
    """
    svc.api.log_api_request(
        app=AppType.Tier2,
        method=HTTPMethod.POST,
        api_path=Path('deploy') / uuid / app_id,
        msg_by_status_code={
            HTTPStatus.OK: 'Recipe deployed to cloudlet.',
            HTTPStatus.NOT_FOUND: 'Failed to create deployment.',
            }
        )
    

@app.command()
def c2():
    """c2"""    
    print('pong')
