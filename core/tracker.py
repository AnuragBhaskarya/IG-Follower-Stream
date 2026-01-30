"""
Main tracker loop - the core logic that all API implementations share.
"""

import time
import random
from typing import Callable, Optional

from .config import (
    CHECK_INTERVAL, RETRY_INTERVAL,
    NOTIFICATION_COOLDOWN
)
from .logger import logger
from .storage import read_stored_followers, write_followers
from .network import is_connected, wait_for_internet
from .notifications import send_notification
from .notification_streaming import get_random_gif
from .audio import play_gain_audio, play_loss_audio


def run_tracker(
    fetch_follower_count: Callable[[], Optional[int]],
    api_name: str = "API"
) -> None:
    """
    Main tracker loop.
    
    Args:
        fetch_follower_count: Function that returns current follower count or None on error.
        api_name: Name of the API for logging purposes.
    """
    logger.info(f"🚀 Starting Instagram Follower Tracker ({api_name})")
    wait_for_internet()

    stored_count = read_stored_followers()
    if stored_count == 0:
        new_count = fetch_follower_count()
        if new_count is not None:
            stored_count = new_count
            write_followers(stored_count)
            logger.info(f"Initialized followers: {stored_count}")
        else:
            logger.error("Failed to initialize, exiting...")
            return
    else:
        logger.info(f"Stored followers: {stored_count}")

    consecutive_failures = 0
    
    while True:
        if not is_connected():
            logger.warning("Internet connection lost. Waiting...")
            wait_for_internet()
            logger.info("Internet connection restored.")
            consecutive_failures = 0

        try:
            new_count = fetch_follower_count()
            
            if new_count is None:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    logger.warning(f"Failed {consecutive_failures} times, waiting longer...")
                    time.sleep(RETRY_INTERVAL * 2)
                else:
                    time.sleep(RETRY_INTERVAL)
                continue
            
            consecutive_failures = 0

            diff = new_count - stored_count
            
            if diff == 0:
                logger.info(f"No change in followers ({new_count}).")
            elif diff > 0:
                unit = "follower" if diff == 1 else "followers"
                message = f"You got {diff} {unit}. Total: {new_count}"
                logger.info(message)
                
                # Get GIF here to ensure we track last used (since tracker process persists)
                gif_path = get_random_gif(is_gain=True)
                send_notification(message, is_gain=True, gif_path=gif_path)
                
                play_gain_audio(diff)
                stored_count = new_count
                write_followers(stored_count)
                # Wait for notification to finish before next check
                time.sleep(NOTIFICATION_COOLDOWN)
            else:
                drop = abs(diff)
                unit = "follower" if drop == 1 else "followers"
                message = f"You lost {drop} {unit}. Total: {new_count}"
                logger.info(message)
                
                # Get GIF here to ensure we track last used
                gif_path = get_random_gif(is_gain=False)
                send_notification(message, is_gain=False, gif_path=gif_path)
                
                play_loss_audio(drop)
                stored_count = new_count
                write_followers(stored_count)
                # Wait for notification to finish before next check
                time.sleep(NOTIFICATION_COOLDOWN)
                        
        except Exception as e:
            logger.error(f"Error during follower count processing: {e}")
            time.sleep(RETRY_INTERVAL)
            
        time.sleep(CHECK_INTERVAL + random.uniform(0, 1))
