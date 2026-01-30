"""
Logging setup for Instagram Follower Tracker.
"""

import logging
from logging.handlers import RotatingFileHandler

from .config import LOG_FILE

# Create logger
logger = logging.getLogger("FollowerTracker")
logger.setLevel(logging.DEBUG)

# File handler with rotation
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
