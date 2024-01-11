from typing import Optional

import logging
from src.tier_shell import strfmt


_DEFAULT_FORMAT = "%(levelname)-8s  %(message)s"


class ApiLoggingFormatter():    
    """Custom formatter class for API logging."""
    def __init__(self, fmt: str = _DEFAULT_FORMAT) -> None:
        self.fmt = fmt

    def format(self, record):
        FORMATS = {
            logging.DEBUG: strfmt.magenta(self.fmt),
            logging.INFO: strfmt.white(self.fmt),
            logging.WARNING: strfmt.yellow(self.fmt),
            logging.ERROR: strfmt.red(self.fmt),
            logging.CRITICAL: strfmt.red(self.fmt),
        }
        
        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_api_logger(
    name: str,
    level: Optional[str] = logging.INFO, 
    fmt: Optional[str] = _DEFAULT_FORMAT,
) -> logging.Logger:
    """Get instance of API logging object"""
    # Create logging object with given name
    logger = logging.getLogger(name)

    # Add print format for stdout
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(ApiLoggingFormatter(fmt))
    
    # Set format and set logging level
    logger.addHandler(ch)
    logger.setLevel(level)
    
    return logger


# lg = get_stdout_logger('test')
# lg.debug("This is a debug message")
# lg.info("This is an info message")
# lg.warning("This is a warning message")
# lg.error("This is an error message")
# lg.critical("This is a critical message")
