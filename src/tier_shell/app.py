import typer

from dependency_injector.wiring import Provide, inject
from src.tier_shell.domain.di import AppDI

from src.domain.logger import get_default_logger
from src.tier_shell.domain.config import Config
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
            'src.tier_shell.service.api'
            ]
        )


# Dependency injector doesn't play well with Typer, cannot stack decorator
# Separating functions seems like the best option for the moment.
@inject
def _app_state(config: Config = Provide[AppDI.config]):
    print(repr(config))


@app.command()
def app_state():
    """Report application state."""
    _app_state()


if __name__ == "__main__":
    app()
