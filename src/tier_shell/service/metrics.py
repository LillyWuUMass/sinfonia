"""Application metrics
"""
from dependency_injector.wiring import Provide, inject
from src.tier_shell.domain.di import AppDI


from src.tier_shell.domain.config import Config


@inject
def get_application_state(config: Config = Provide[AppDI.config]):
    print(repr(config))
    