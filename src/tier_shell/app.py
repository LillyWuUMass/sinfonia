from dependency_injector.wiring import Provide, inject

from src.tier_shell.domain.config import Config
from src.tier_shell.domain.di import AppDI


def build():
    app = AppDI()
    app.config_yaml.from_yaml('src/tier_shell/config.yml')
    app.init_resources()
    app.wire(modules=[__name__])


@inject
def test(
    config: Config = Provide[AppDI.config]
):
    print(config.tier1)


if __name__ == "__main__":
    build()
    test()
