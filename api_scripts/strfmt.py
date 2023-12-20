from http import HTTPStatus
from typing import Optional
from pprint import PrettyPrinter

from colorama import Fore, Back


# Format strings
_BOLD = '\033[1m'
_END = '\033[0m'


# Pretty printer formatter for JSON
_pp = PrettyPrinter(indent=4, width=160)


def white(*tp) -> str:
    t = ' '.join(tp)
    return Fore.WHITE + t + Fore.RESET


def cyan(*tp) -> str:
    t = ' '.join(tp)
    return Fore.LIGHTCYAN_EX + t + Fore.RESET


def magenta(*tp) -> str:
    t = ' '.join(tp)
    return Fore.LIGHTMAGENTA_EX + t + Fore.RESET


def cyan_bg(*tp) -> str:
    t = ' '.join(tp)
    return Back.LIGHTCYAN_EX + t + Back.RESET
    
    
def red(*tp) -> str:
    t = ' '.join(tp)
    return Fore.RED + t + Fore.RESET
    
    
def red_bg(*tp) -> str:
    t = ' '.join(tp)
    return Back.RED + Fore.BLACK + t + Fore.RESET + Back.RESET
    
    
def green(*tp) -> str:
    t = ' '.join(tp)
    return Fore.LIGHTGREEN_EX + t + Fore.RESET
    
    
def green_bg(*tp) -> str:
    t = ' '.join(tp)
    return Back.LIGHTGREEN_EX + Fore.WHITE + t + Fore.RESET + Back.RESET
    
    
def yellow(*tp) -> str:
    t = ' '.join(tp)
    return Fore.LIGHTYELLOW_EX + t + Fore.RESET


def bold(*tp) -> str:
    t = ' '.join(tp)
    return _BOLD + t + _END



def http_status_code(code: int) -> str:
    s = bold(f"{str(code)} {HTTPStatus(code).phrase}")
    if code >= 200 and code <= 299:
        return green(s)
    elif code >= 500 and code <= 599:
        return red(s)
    
    return yellow(s)


def json(j: str) -> str:
    return _pp.pformat(j)
