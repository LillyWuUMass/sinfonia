import typer

from src.tier_shell.domain.di import AppDI

import src.tier_shell.service as svc
import src.tier_shell.view as view


app = typer.Typer()
app.add_typer(view.tier1.app, name='tier1')
app.add_typer(view.tier2.app, name='tier2')


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
    svc.metrics.get_application_state()


if __name__ == "__main__":
    app()
