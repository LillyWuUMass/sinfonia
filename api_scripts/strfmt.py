from http import HTTPStatus
from typing import Optional
from pprint import PrettyPrinter

import api_scripts.style_printer as sp


_pp = PrettyPrinter(indent=4)


def http_status_code(code: int) -> str:
    s = f"{str(code)} {HTTPStatus(code).phrase}"
    if code >= 200 and code <= 299:
        return sp.bold(sp.green(s))
    elif code >= 400 and code <= 599:
        return sp.bold(sp.red(s))
    
    return sp.bold(sp.yellow(s))


def json(j: str) -> str:
    return _pp.pformat(j)
