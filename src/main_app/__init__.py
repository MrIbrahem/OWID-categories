""" """

from .logger_config import configure_logging
from .owid_config import LOGGER_LEVEL

configure_logging(LOGGER_LEVEL, use_colorlog=True)

__all__ = []
