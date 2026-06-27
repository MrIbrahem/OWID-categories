#!/usr/bin/env python3
"""

python src/dj.py

"""

import logging

from me1 import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(log_color)s%(levelname)-s %(reset)s- [%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
