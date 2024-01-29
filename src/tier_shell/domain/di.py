"""Dependecy injection"""

import logging.config

from dependency_injector import containers, providers

from src.tier_shell.domain.gateway import APIGateway


class AppDI(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    logger = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
        )
    
    # Gateways
    
    api = providers.Singleton(APIGateway)
    