"""Application metrics
"""
from dependency_injector.wiring import Provide, inject
from src.tier_shell.domain.di import AppDI

import src.lib.str.format as strfmt
from src.tier_shell.domain.config import AppConfig


@inject
def get_application_state(
        config_tier1: AppConfig = Provide[AppDI.config_tier1],
        config_tier2: AppConfig = Provide[AppDI.config_tier2]
):
    print(strfmt.white('Tier 1'))
    print(strfmt.white(repr(config_tier1)))
    print(strfmt.white('Tier 2'))
    print(strfmt.white(repr(config_tier2)))
    