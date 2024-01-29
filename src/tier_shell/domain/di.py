"""Dependecy injection"""

import logging.config

from dependency_injector import containers, providers

from src.tier_shell.domain.config import Config
from src.tier_shell.domain.gateway import APIGateway


class AppDI(containers.DeclarativeContainer):    
    # Core
    
    config_yaml = providers.Configuration()
    
    config = providers.Singleton(
        Config.model_validate,
        config_yaml,
        )
    
    logger = providers.Resource(
        logging.config.dictConfig,
        config=config_yaml.logging,
        )
    
    # Gateways
    
    api = providers.Singleton(APIGateway)
    