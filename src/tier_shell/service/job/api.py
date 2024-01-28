"""Manages life cycle of API jobs

This module contains life cycle scripts to streamline the implementation of new
commands. As of writing, we assume HTTP/JSON to be the data transfer medium for 
all client-server communications.
"""
from typing import Optional, Dict

import logging
import requests

from yarl import URL

from src.lib.http import HTTPMethod
from src.domain.logger import get_default_logger


# TODO
def log_api_request(
        u: URL,
        method: HTTPMethod,
        is_verbose: bool = True,
        logger: Optional[logging.Logger] = None,
        resp_msg: Optional[Dict[str, str]] = None,
) -> requests.Response:
    if not logger:
        logger = get_default_logger()
        
    if not resp_msg:
        resp_msg = dict()
        
    if is_verbose:
        logger.info(f'Sending {method} request to {u} ...')

    raise NotImplementedError()
