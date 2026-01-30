"""
File storage utilities for follower count persistence.
"""

import os
from .config import FOLLOWERS_FILE
from .logger import logger


def read_stored_followers(filepath: str = FOLLOWERS_FILE) -> int:
    """Reads the stored follower count from file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read().strip()
                return int(content.replace(",", "")) if content else 0
    except Exception as e:
        logger.error(f"Reading file error: {e}")
    return 0


def write_followers(count: int, filepath: str = FOLLOWERS_FILE) -> None:
    """Writes the current follower count to file."""
    try:
        with open(filepath, 'w') as f:
            f.write(str(count))
    except Exception as e:
        logger.error(f"Writing file error: {e}")
