""" """

from .logger_config import configure_logging
from .owid_config import LOGGER_LEVEL, LOG_DIR

configure_logging(
    LOGGER_LEVEL,
    LOG_DIR,
    use_colorlog=True,
)

__all__ = []
