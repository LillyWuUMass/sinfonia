import typer
from src.tier_shell.domain.di import AppDI


cli = typer.Typer('tier1')


def build():
    app = AppDI()
    app.init_resource()
    app.wire(modules=['app'])


if __name__ == "__main__":
    build()
    cli()
