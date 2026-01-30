"""
Core configuration for Instagram Follower Tracker
All paths are dynamic, relative to this file's location.
"""

import os

# ---------------------------
# Dynamic Path Configuration
# ---------------------------
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CORE_DIR)
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
LOG_FILE = os.path.join(PROJECT_DIR, "log.txt")
FOLLOWERS_FILE = os.path.join(PROJECT_DIR, "followers.txt")

# Intro audio files
AUDIO_GET = os.path.join(AUDIO_DIR, "get.mp3")
AUDIO_LOST = os.path.join(AUDIO_DIR, "lost.mp3")

# ---------------------------
# Tracker Settings
# ---------------------------
INSTAGRAM_USERNAME = "ishowspeed"
CHECK_INTERVAL = 1        # seconds between each check
RETRY_INTERVAL = 5        # seconds to wait on error
AUDIO_OVERLAY_DELAY = 1 # seconds before voice plays after intro

# Note: No artificial thresholds - works for any follower count
# ---------------------------
# Notification Settings
# ---------------------------
GAIN_GIF_SIZE = 150   # Size of gain.gif (pixels)
GAIN_PNG_SIZE = 100   # Size of gain.png (pixels)
LOSS_GIF_SIZE = 150   # Size of loss.gif (pixels)
LOSS_PNG_SIZE = 100   # Size of loss.png (pixels)

# Position from top-right corner (pixels)
# Decrease NOTIF_RIGHT_OFFSET to move more right (closer to edge)
# Decrease NOTIF_TOP_OFFSET to move more up (closer to top)
NOTIF_RIGHT_OFFSET = -20  # Distance from right edge
NOTIF_TOP_OFFSET = 0    # Distance from top edge

# Cooldown after notification (seconds) - prevents overlapping notifications
NOTIFICATION_COOLDOWN = 5  # Should be >= notification duration (~5s) + buffer

# Font settings
NOTIF_FONT_FAMILY = "Arial Black"  # Font family (e.g., "Arial", "Impact", "Comic Sans MS")
NOTIF_LINE1_SIZE = 20              # Font size for line 1 (e.g., "You got 3 followers")
NOTIF_LINE2_SIZE = 18              # Font size for line 2 (e.g., "Total: 54174")
NOTIF_LINE_SPACING = 1             # Spacing between lines (pixels, lower = tighter)

# ---------------------------
# Audio Directory Mappings (dynamic paths)
# ---------------------------
AUDIO_DIRS_GAIN = {
    1: os.path.join(AUDIO_DIR, "gain", "1"),
    2: os.path.join(AUDIO_DIR, "gain", "2"),
    3: os.path.join(AUDIO_DIR, "gain", "3"),
    4: os.path.join(AUDIO_DIR, "gain", "4"),
    5: os.path.join(AUDIO_DIR, "gain", "5"),
    6: os.path.join(AUDIO_DIR, "gain", "6"),
    7: os.path.join(AUDIO_DIR, "gain", "7"),
    8: os.path.join(AUDIO_DIR, "gain", "8"),
    9: os.path.join(AUDIO_DIR, "gain", "9"),
    10: os.path.join(AUDIO_DIR, "gain", "10"),
    "more_than_10": os.path.join(AUDIO_DIR, "gain", "more_than_10"),
    "more_than_100": os.path.join(AUDIO_DIR, "gain", "more_than_100"),
    "more_than_500": os.path.join(AUDIO_DIR, "gain", "more_than_500"),
    "more_than_1000": os.path.join(AUDIO_DIR, "gain", "more_than_1000"),
    "more_than_2000": os.path.join(AUDIO_DIR, "gain", "more_than_2000"),
    "more_than_5000": os.path.join(AUDIO_DIR, "gain", "more_than_5000"),
}

AUDIO_DIRS_LOSS = {
    1: os.path.join(AUDIO_DIR, "lost", "1"),
    2: os.path.join(AUDIO_DIR, "lost", "2"),
}
