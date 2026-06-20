#!/usr/bin/env python3
"""

python src/dj.py

"""

import logging

from main_app.logger_config import setup_logging
from main_app.dj.me1 import main

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging(
        level="INFO",
        name="main_app",
        use_colorlog=False,
        overwrite=True,
        use_console=False,
    )
    main()
