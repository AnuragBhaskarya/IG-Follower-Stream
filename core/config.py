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
# Directory containing generated TTS files
GENERATED_AUDIO_DIR = os.path.join(AUDIO_DIR, "generated")
