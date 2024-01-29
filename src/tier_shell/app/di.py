"""Dependecy injection"""

import logging.config

from dependency_injector import containers, providers


class App(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    logger = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
        )
    