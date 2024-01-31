import typer

from src.tier_shell.domain.di import AppDI

from src.lib.http import HTTPMethod, HTTPStatus
from src.domain.logger import get_default_logger

import src.tier_shell.service.metrics as svc_metrics
import src.tier_shell.service.api as svc_api
from src.tier_shell.view.tier1 import app as tier1_app
from src.tier_shell.view.tier2 import app as tier2_app


app = typer.Typer()
app.add_typer(tier1_app, name='tier1')
app.add_typer(tier2_app, name='tier2')


logger = get_default_logger()


@app.callback()
def build():
    """Build application."""    
    app = AppDI()
    app.config_dict.from_yaml('src/tier_shell/config.yml')
    app.init_resources()
    app.wire(
        modules=[
            __name__, 
            'src.tier_shell.view.tier1',
            'src.tier_shell.view.tier2',
            'src.tier_shell.service.api',
            'src.tier_shell.service.metrics',
            ]
        )


# Dependency injector doesn't play well with Typer, cannot stack decorator
# Separating functions seems like the best option for the moment.
@app.command()
def app_state():
    """Report application state."""
    svc_metrics.get_application_state()


if __name__ == "__main__":
    app()
