"""
Desktop notification utilities.
Uses streaming-style overlay notifications.
"""

import subprocess
from .logger import logger

# Use streaming-style notifications
USE_STREAMING = True


def send_notification(message: str, title: str = "Instagram Followers", is_gain: bool = True, gif_path: str = None) -> None:
    """
    Sends a desktop notification.
    Uses streaming-style overlay if enabled.
    """
    if USE_STREAMING:
        try:
            from .notification_streaming import show_streaming_notification
            show_streaming_notification(message, is_gain, gif_path)
            return
        except Exception as e:
            logger.warning(f"Streaming notification failed: {e}")
    
    # Fallback to basic notify-send
    try:
        subprocess.run(["notify-send", title, message], check=True)
    except Exception as e:
        logger.error(f"Notification error: {e}")
