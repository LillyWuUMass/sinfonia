import logging

import lib.str.format as strfmt


_DEFAULT_FORMAT = "%(asctime)s  %(name)s  %(levelname)s  %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _color_by_log_level(s: str, level: int) -> str:
    match level:
        case logging.DEBUG:
            return strfmt.magenta(s)
        case logging.INFO:
            return strfmt.white(s)
        case logging.WARNING:
            return strfmt.yellow(s)
        case logging.ERROR:
            return strfmt.red(s)
        case logging.CRITICAL:
            return strfmt.red(s)
        case _:
            return strfmt.white(s)


class DefaultFormatter(logging.Formatter):
    """Custom formatter class for API logging."""
    def __init__(self, 
            fmt: str = _DEFAULT_FORMAT,
            datefmt: str = _DEFAULT_DATE_FORMAT,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord):                
        return _color_by_log_level(super().format(record), record.levelno)
