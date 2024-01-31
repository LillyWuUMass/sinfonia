"""Application metrics
"""
from dependency_injector.wiring import Provide, inject
from src.tier_shell.domain.di import AppDI

import src.domain.format as fmt
from src.tier_shell.domain.config import AppConfig


@inject
def get_application_state(
        config_tier1: AppConfig = Provide[AppDI.config_tier1],
        config_tier2: AppConfig = Provide[AppDI.config_tier2]
):
    print(fmt.str.white('Tier 1'))
    print(fmt.str.white(repr(config_tier1)))
    print(fmt.str.white('Tier 2'))
    print(fmt.str.white(repr(config_tier2)))
    