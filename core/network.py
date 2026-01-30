"""
Network utilities for internet connectivity checks.
"""

import time
import requests
from .logger import logger


def is_connected() -> bool:
    """Checks for an active internet connection."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False


def wait_for_internet() -> None:
    """Waits until an internet connection is detected."""
    while not is_connected():
        logger.warning("No internet connection. Retrying in 10 seconds...")
        time.sleep(10)
