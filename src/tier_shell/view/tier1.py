import typer

from src.lib.http import HTTPMethod, HTTPStatus

import src.tier_shell.service as svc


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier1 instances.",
    )


@app.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    svc.api.log_api_request(
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
