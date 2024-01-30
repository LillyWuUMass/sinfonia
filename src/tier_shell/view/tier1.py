import logging

import typer


from src.domain.logger import get_default_logger
from src.tier_shell.service.api import log_api_request
from src.tier_shell.domain.config import Config


app = typer.Typer(
    name="tier1",
    help="Interactions with Tier1 instances.",
    )


logger = get_default_logger()


@app.command()
def get_known_cloudlets():
    """Return manifest of known Tier 2 cloudlets."""
    pass
    

@app.command()
def c2():
    """c2"""    
    print('world')
