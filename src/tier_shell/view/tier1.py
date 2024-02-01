from pathlib import Path

import typer

from src.lib.http import HTTPMethod, HTTPStatus

from src.tier_shell.domain.app import AppType

import src.tier_shell.service as svc

from src.tier_shell.view.common import (
    uuid_option,
    app_id_option,
    )


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier 1 instances.",
    )


@app.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    svc.api.log_api_request(
        app=AppType.Tier1,
        method=HTTPMethod.GET,
        api_path='cloudlets',
        msg_by_status_code={
            HTTPStatus.OK: 'Returning list of known cloudlets'
            }
        )


@app.command()
def update_cloudlet_resource_metrics():
    """Update cloudlet resource metrics."""
    raise NotImplementedError()


@app.command()
def get_deployment_recipe(uuid: str = uuid_option):
    """Retrieve information on deployment recipes."""
    svc.api.log_api_request(
        app=AppType.Tier1,
        method=HTTPMethod.GET,
        api_path=Path('recipes') / uuid,
        msg_by_status_code={
            HTTPStatus.OK: 'Returning list of known cloudlets.',
            HTTPStatus.FORBIDDEN: 'Cannot access deployment recipe.',
            HTTPStatus.NOT_FOUND: 'Deployment recipe not found.',
            }
        )
