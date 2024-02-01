import typer

from dependency_injector.wiring import Provide, inject

import src.domain.format as fmt

from src.tier_shell.domain.config import AppConfig
from src.tier_shell.domain.di import AppDI

import src.tier_shell.view as view


app = typer.Typer()
app.add_typer(view.tier1.app, name='tier1')
app.add_typer(view.tier2.app, name='tier2')


@app.command()
def app_state():
    """Report application state."""
    # Dependency injector doesn't play well with Typer, cannot stack decorator
    # Separating functions seems like the best option for the moment.
    _app_state()

    
@inject
def _app_state(
        config_tier1: AppConfig = Provide[AppDI.config_tier1],
        config_tier2: AppConfig = Provide[AppDI.config_tier2]
):
    print(fmt.str.white('Tier 1'))
    print(fmt.str.white(repr(config_tier1)))
    print(fmt.str.white('Tier 2'))
    print(fmt.str.white(repr(config_tier2)))


@app.callback()
def build():
    app_di = AppDI()
    app_di.config_dict.from_yaml('src/tier_shell/config.yml')
    app_di.init_resources()
    
    # Only inject dependencies to View layer.
    # This is to avoid reverse dependency from View to Service layer.
    app_di.wire(
        modules=[
            __name__, 
            'src.tier_shell.view.tier1',
            'src.tier_shell.view.tier2',
            ]
        )


if __name__ == "__main__":
    app()
