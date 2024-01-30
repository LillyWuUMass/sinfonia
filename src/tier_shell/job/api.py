"""Manages life cycle of API jobs

This module contains life cycle scripts to streamline the implementation of new
commands. As of writing, we assume HTTP/JSON to be the data transfer medium for 
all client-server communications.
"""
from typing import Optional, Dict

import logging
import requests

from yarl import URL

import src.lib.http as httplib
import src.lib.http.format as httpfmt
import src.lib.str.format as strfmt
from src.domain.logger import get_default_logger

from src.tier_shell.domain.config import AppConfig


_TIMEOUT_ERR_MSG = lambda sec: f"api timeout exceeded ({sec} seconds)"
_CONNECTION_ERR_MSG = "api timeout exceeded"
_ERR_MSG = "an exception occurred"


def _short_msg_critical(
        config: AppConfig,
        method: httplib.HTTPMethod,
        msg: str = '',
):
    host_url_repr = str(config.root_url)
    
    method_repr = str(method)
    req_path_repr = config.api_path
    req_repr = f"{method_repr} {req_repr}"
    req_repr = strfmt.bold(strfmt.magenta(req_repr))
    
    return f"{host_url_repr} - {req_repr} - ERROR - {msg}"


def _short_msg_log(
        config: AppConfig,
        method: httplib.HTTPMethod,
        status_code: int,
        msg: str = '',
):
    host_url_repr = str(config.root_url)
    
    method_repr = str(method)
    req_path_repr = config.api_path
    req_repr = f"{method_repr} {req_repr}"
    req_repr = strfmt.bold(strfmt.magenta(req_repr))

    status_code_repr = httplib.status_code_repr(status_code)
    
    return f"{host_url_repr} - {req_repr} - {status_code_repr} - {msg}"


def log_api_request(
        config: AppConfig,
        method: httplib.HTTPMethod,
        is_short_form: bool = True,
        logger: Optional[logging.Logger] = get_default_logger(),
        msg_by_status_code: Optional[Dict[int, str]] = None,
):
    if not resp_msg:
        resp_msg = dict()
        
    u: URL = URL(config.root_url) / config.api_path
    u.with_port(config.port)
    url_repr = strfmt.bold(strfmt.magenta(str(u)))
    
    ts: int = config.timeout_seconds
        
    if not is_short_form:
        logger.info(f"Sending {method} request to {url_repr} ...")
    
    # Make API request
        
    err_msg, stack_trace: str = '', ''
    try:
        resp = requests.get(u, timeout=config.timeout_seconds)
    except requests.Timeout:
        err_msg = _TIMEOUT_ERR_MSG(ts)
    except requests.ConnectionError as e:
        err_msg, stack_trace = _CONNECTION_ERR_MSG, str(e)
    except requests.RequestException as e:
        err_msg, stack_trace = _ERR_MSG, str(e)

    # Log error if exists

    if err_msg:
        if not is_short_form:
            logger.critical(err_msg)
        else:
            logger.critical(_short_msg_critical(config, method, err_msg))
            
        if stack_trace:
            logger.debug(stack_trace)
            
        raise Exception()

    # Log response

    status_code = resp.status_code
    status_code_repr = httpfmt.status_code_repr(status_code)
    
    if is_short_form:
        logger.info(_short_msg_log(config, method))
        return
    
    description = msg_by_status_code.get(status_code, '')
    
    msg = f"{status_code_repr}" + (f" -- {description}" if description else '')
    if httplib.is_json_response(resp):
        msg += "\n" + httplib.json_repr(resp.json())

    logger.info(msg)
