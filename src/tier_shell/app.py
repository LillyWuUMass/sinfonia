from dataclasses import dataclass

import logging

from src.tier_shell.config import AppConfig


@dataclass(init=True)
class App:
    config: AppConfig
    log: logging.Logger
    