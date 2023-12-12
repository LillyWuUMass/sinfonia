from typing import Optional
from pprint import PrettyPrinter

import api_scripts.style_printer as sp


_pp = PrettyPrinter(indent=4)


def http_status_code(code: int) -> str:
    if code >= 200 and code <= 299:
        return sp.bold(sp.green(str(code)))
    elif code >= 400 and code <= 599:
        return sp.bold(sp.red(str(code)))
    
    return sp.bold(sp.yellow(str(code)))


def json(j: str) -> str:
    return _pp.pformat(j)
