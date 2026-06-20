""" """

from .logger_config import configure_logging
from .owid_config import LOG_DIR, LOGGER_LEVEL

configure_logging(
    LOGGER_LEVEL,
    LOG_DIR,
    use_colorlog=True,
)

__all__ = []
