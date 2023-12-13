from typing import Any, Optional, Mapping

import logging
import style_printer as sp


_DEFAULT_FORMAT = "%(levelname)-8s  %(message)s"


class ApiLoggingFormatter():    
    def __init__(self, fmt: str = _DEFAULT_FORMAT) -> None:
        self.fmt = fmt

    def format(self, record):
        FORMATS = {
            logging.DEBUG: sp.magenta(self.fmt),
            logging.INFO: sp.white(self.fmt),
            logging.WARNING: sp.yellow(self.fmt),
            logging.ERROR: sp.red(self.fmt),
            logging.CRITICAL: sp.red(self.fmt),
        }
        
        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_stdout_logger(
    name: str,
    level: Optional[str] = logging.INFO, 
    format: Optional[str] = _DEFAULT_FORMAT,
) -> logging.Logger:
    """Get formatted Python logging object instance"""
    # Create logging object with given name
    logger = logging.getLogger(name)

    # Add print format for stdout
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(ApiLoggingFormatter())
    
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
