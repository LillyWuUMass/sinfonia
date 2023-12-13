from http import HTTPStatus
from typing import Optional
from pprint import PrettyPrinter

import api_scripts.style_printer as sp


_pp = PrettyPrinter(indent=4, width=160)


def http_status_code(code: int) -> str:
    s = sp.bold(f"{str(code)} {HTTPStatus(code).phrase}")
    if code >= 200 and code <= 299:
        return sp.green(s)
    elif code >= 500 and code <= 599:
        return sp.red(s)
    
    return sp.yellow(s)


def json(j: str) -> str:
    return _pp.pformat(j)
