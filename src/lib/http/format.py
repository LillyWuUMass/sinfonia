from http import HTTPStatus
from pprint import PrettyPrinter


# Pretty printer formatter for JSON
_pp = PrettyPrinter(indent=2, width=90)


def http_repr(code: int) -> str:
    """Return HTTP code along with its descriptive phrase.
    
    Args:
        code -- int: HTTP status code
        
    Return:
        str
    """
    return f"{str(code)} {HTTPStatus(code).phrase}"


def json_repr(j: str) -> str:
    """Prettify JSON string.
    
    Args:
        j -- str: JSON string
        
    Return:
        str
    """    
    return _pp.format(j)
