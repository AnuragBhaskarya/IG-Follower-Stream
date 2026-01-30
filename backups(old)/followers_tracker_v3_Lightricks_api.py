#!/usr/bin/env python3
"""
Instagram Follower Tracker v3 - Using Lightricks/PopularPays API
Even simpler - just a single GET request, no CSRF token needed!
"""

import time
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import random
import requests
import threading

# ---------------------------
# Dynamic Path Configuration
# ---------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "audio")
LOG_FILE = os.path.join(SCRIPT_DIR, "log.txt")
FOLLOWERS_FILE = os.path.join(SCRIPT_DIR, "followers.txt")

# Intro audio files
AUDIO_GET = os.path.join(AUDIO_DIR, "get.mp3")
AUDIO_LOST = os.path.join(AUDIO_DIR, "lost.mp3")

# ---------------------------
# Logging Setup
# ---------------------------
logger = logging.getLogger("FollowerTracker")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

# ---------------------------
# Configuration
# ---------------------------
INSTAGRAM_USERNAME = "knowledgemaxxing"
API_URL = "https://social-media-users-data-api-production.lightricks.workers.dev/instagram"
CHECK_INTERVAL = 1        # minimal delay - poll immediately after response
RETRY_INTERVAL = 5        # seconds to wait on error
AUDIO_OVERLAY_DELAY = 1.5  # seconds before voice plays after intro

# Thresholds for ignoring glitches
MAX_INCREASE_THRESHOLD = 50000
MIN_FOLLOWERS = 1
MAX_FOLLOWERS = 500000

# ---------------------------
# Audio Directory Mapping for Gains (dynamic paths)
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

# ---------------------------
# Audio Directory Mapping for Losses (dynamic paths)
# ---------------------------
AUDIO_DIRS_LOSS = {
    1: os.path.join(AUDIO_DIR, "lost", "1"),
    2: os.path.join(AUDIO_DIR, "lost", "2"),
}

last_played_gain = {}
last_played_loss = {}

# Session for persistent cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://popularpays.com",
    "Referer": "https://popularpays.com/",
})

# ---------------------------
# Internet Connectivity Functions
# ---------------------------
def is_connected() -> bool:
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

def wait_for_internet() -> None:
    while not is_connected():
        logger.warning("No internet connection. Retrying in 10 seconds...")
        time.sleep(10)

# ---------------------------
# File Utilities
# ---------------------------
def read_stored_followers(file_path: str) -> int:
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return int(f.read().strip())
    except Exception as e:
        logger.error(f"Reading file error: {e}")
    return 0

def write_followers(file_path: str, count: int) -> None:
    try:
        with open(file_path, 'w') as f:
            f.write(str(count))
    except Exception as e:
        logger.error(f"Writing file error: {e}")

# ---------------------------
# API Function (Super Simple!)
# ---------------------------
def fetch_follower_count() -> Optional[int]:
    """Fetches the follower count using Lightricks API - single GET request!"""
    try:
        response = session.get(
            API_URL,
            params={"username": INSTAGRAM_USERNAME},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            followers = data.get("followersCount")
            if isinstance(followers, int):
                return followers
            logger.warning(f"Unexpected followers value: {followers}")
        else:
            logger.error(f"API returned status {response.status_code}")
            
        return None
    except Exception as e:
        logger.error(f"Error fetching follower count: {e}")
        return None

# ---------------------------
# Notification Function
# ---------------------------
def send_notification(message: str) -> None:
    try:
        subprocess.run(["notify-send", "Instagram Followers", message], check=True)
    except Exception as e:
        logger.error(f"Notification error: {e}")

# ---------------------------
# Audio Functions
# ---------------------------
def get_random_audio(folder_path: str, category_key: str, last_played_dict: dict) -> str:
    try:
        if not os.path.exists(folder_path):
            logger.warning(f"Audio folder not found: {folder_path}")
            return ""
        files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
        if not files:
            return ""
        if category_key in last_played_dict and last_played_dict[category_key] in files and len(files) > 1:
            files.remove(last_played_dict[category_key])
        selected = random.choice(files)
        last_played_dict[category_key] = selected
        return os.path.join(folder_path, selected)
    except Exception as e:
        logger.error(f"Error selecting random audio from {folder_path}: {e}")
        return ""

def play_audio(audio_path: str) -> None:
    if audio_path and os.path.exists(audio_path):
        subprocess.Popen(["mpv", "--no-terminal", audio_path])
    else:
        logger.warning(f"Audio file not found: {audio_path}")

def play_audio_with_overlay(intro_path: str, voice_path: str, delay: float = AUDIO_OVERLAY_DELAY) -> None:
    """Plays intro audio, then overlays voice after delay."""
    def delayed_voice():
        time.sleep(delay)
        if voice_path and os.path.exists(voice_path):
            subprocess.Popen(["mpv", "--no-terminal", voice_path])
    
    if intro_path and os.path.exists(intro_path):
        subprocess.Popen(["mpv", "--no-terminal", intro_path])
    
    if voice_path:
        threading.Thread(target=delayed_voice, daemon=True).start()

def play_gain_audio(diff: int) -> None:
    if diff <= 10:
        category = diff
    elif diff <= 100:
        category = "more_than_10"
    elif diff <= 500:
        category = "more_than_100"
    elif diff <= 1000:
        category = "more_than_500"
    elif diff <= 2000:
        category = "more_than_1000"
    elif diff <= 5000:
        category = "more_than_2000"
    else:
        category = "more_than_5000"

    if category in AUDIO_DIRS_GAIN:
        folder = AUDIO_DIRS_GAIN[category]
        voice_audio = get_random_audio(folder, str(category), last_played_gain)
        play_audio_with_overlay(AUDIO_GET, voice_audio)

def play_loss_audio(diff: int) -> None:
    if diff not in (1, 2):
        return
    if diff in AUDIO_DIRS_LOSS:
        folder = AUDIO_DIRS_LOSS[diff]
        voice_audio = get_random_audio(folder, str(diff), last_played_loss)
        play_audio_with_overlay(AUDIO_LOST, voice_audio)

# ---------------------------
# Main Function
# ---------------------------
def main() -> None:
    logger.info("🚀 Starting Instagram Follower Tracker v3 (Lightricks API)")
    wait_for_internet()

    stored_count = read_stored_followers(FOLLOWERS_FILE)
    if stored_count == 0:
        new_count = fetch_follower_count()
        if new_count is not None:
            stored_count = new_count
            write_followers(FOLLOWERS_FILE, stored_count)
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

            if new_count <= MIN_FOLLOWERS or new_count > MAX_FOLLOWERS:
                logger.warning(f"Implausible follower count: {new_count}. Skipping update.")
                time.sleep(CHECK_INTERVAL + random.uniform(0, 2))
                continue

            diff = new_count - stored_count
            if diff == 0:
                logger.info(f"No change in followers ({new_count}).")
            elif diff > 0:
                if diff > MAX_INCREASE_THRESHOLD:
                    logger.warning(f"Follower spike too high ({diff}). Skipping update.")
                else:
                    unit = "follower" if diff == 1 else "followers"
                    message = f"You got {diff} {unit}. Total: {new_count}"
                    logger.info(message)
                    send_notification(message)
                    play_gain_audio(diff)
                    stored_count = new_count
                    write_followers(FOLLOWERS_FILE, stored_count)
            else:
                drop = abs(diff)
                if drop > MAX_INCREASE_THRESHOLD:
                    logger.warning(f"Follower drop too high ({drop}). Skipping update.")
                else:
                    unit = "follower" if drop == 1 else "followers"
                    message = f"You lost {drop} {unit}. Total: {new_count}"
                    logger.info(message)
                    send_notification(message)
                    if drop in (1, 2):
                        play_loss_audio(drop)
                    stored_count = new_count
                    write_followers(FOLLOWERS_FILE, stored_count)
                        
        except Exception as e:
            logger.error(f"Error during follower count processing: {e}")
            time.sleep(RETRY_INTERVAL)
            
        time.sleep(CHECK_INTERVAL + random.uniform(0, 2))

if __name__ == "__main__":
    main()
