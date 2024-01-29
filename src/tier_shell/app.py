import logging

import typer

from dependency_injector.wiring import Provide, inject

from src.tier_shell.domain.config import Config
from src.tier_shell.domain.di import AppDI
from src.tier_shell.service.tier1 import app as tier1_app
from src.tier_shell.service.tier2 import app as tier2_app


app = typer.Typer()


def build():
    # Build application dependencies
    app = AppDI()
    app.config_dict.from_yaml('src/tier_shell/config.yml')
    app.init_resources()
    app.wire(modules=[__name__])
    
    
# Register sub-applications
app.add_typer(tier1_app, name='tier1')
app.add_typer(tier2_app, name='tier2')
    
    
@app.command()
def core1():
    pass


@app.command()
def core2():
    pass


if __name__ == "__main__":
    build()
    app()
