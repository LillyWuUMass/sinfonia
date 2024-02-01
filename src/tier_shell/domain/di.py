"""Dependecy injection"""

import logging.config

from dependency_injector import containers, providers

from src.tier_shell.domain.config import Config, AppConfig
from src.tier_shell.domain.gateway import APIGateway


class AppDI(containers.DeclarativeContainer):    
    # Core
    
    config_dict = providers.Configuration()
    
    config = providers.Singleton(
        Config.model_validate,
        config_dict,
        )
    
    config_tier1 = providers.Singleton(
        AppConfig.model_validate,
        config_dict.tier1,
        )
    
    config_tier2 = providers.Singleton(
        AppConfig.model_validate,
        config_dict.tier2,
        )
    
    logging = providers.Resource(
        logging.config.dictConfig,
        config_dict.logging,
        )
    
    # Gateways
    
    api = providers.Singleton(APIGateway)
    