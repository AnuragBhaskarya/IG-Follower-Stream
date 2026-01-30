# ---------------------------
# safe method using blastup.com
# ---------------------------

#!/usr/bin/env python3
import time
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import random
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------------------
# Logging Setup
# ---------------------------
logger = logging.getLogger("IGBlastupTracker")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("/home/so9ic/pytools/followers_tracker/log.txt", maxBytes=10*1024*1024, backupCount=0)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ---------------------------
# Configuration
# ---------------------------
BLASTUP_URL = "https://blastup.com/instagram-follower-count?knowledgemaxxing"
FOLLOWERS_FILE = "/home/so9ic/pytools/followers_tracker/followers.txt"
CHECK_INTERVAL = 10       # seconds between each check (blastup page updates every 10 sec)
RETRY_INTERVAL = 5        # seconds to wait on error

# Thresholds for ignoring glitches
MAX_DROP_THRESHOLD = 3
MAX_INCREASE_THRESHOLD = 10000
MIN_FOLLOWERS = 1
MAX_FOLLOWERS = 100000

# ---------------------------
# Audio Directory Mapping for Gains
# ---------------------------
# For follower gains of 1 to 10, and checkpoints for larger gains,
# each key here points to a folder containing 5 different tone files.
AUDIO_DIRS_GAIN = {
    1: "/home/so9ic/pytools/followers_tracker/audio_gain_1",
    2: "/home/so9ic/pytools/followers_tracker/audio_gain_2",
    3: "/home/so9ic/pytools/followers_tracker/audio_gain_3",
    4: "/home/so9ic/pytools/followers_tracker/audio_gain_4",
    5: "/home/so9ic/pytools/followers_tracker/audio_gain_5",
    6: "/home/so9ic/pytools/followers_tracker/audio_gain_6",
    7: "/home/so9ic/pytools/followers_tracker/audio_gain_7",
    8: "/home/so9ic/pytools/followers_tracker/audio_gain_8",
    9: "/home/so9ic/pytools/followers_tracker/audio_gain_9",
    10: "/home/so9ic/pytools/followers_tracker/audio_gain_10",
    "more_than_10": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_10",
    "more_than_100": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_100",
    "more_than_500": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_500",
    "more_than_1000": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_1000",
    "more_than_2000": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_2000",
    "more_than_5000": "/home/so9ic/pytools/followers_tracker/audio_gain_more_than_5000",
}

# ---------------------------
# Audio Directory Mapping for Losses
# ---------------------------
# Only two loss categories: losing 1 follower and losing 2 followers.
AUDIO_DIRS_LOSS = {
    1: "/home/so9ic/pytools/followers_tracker/audio_lost_1",
    2: "/home/so9ic/pytools/followers_tracker/audio_lost_2",
}

# Global dictionaries to store the last played file for each category
last_played_gain = {}
last_played_loss = {}

# ---------------------------
# Internet Connectivity Functions
# ---------------------------
def is_connected() -> bool:
    """Checks for an active internet connection by making a simple GET request."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False

def wait_for_internet() -> None:
    """Waits in 10-second intervals until an internet connection is detected."""
    while not is_connected():
        logger.warning("No internet connection. Retrying in 10 seconds...")
        time.sleep(10)

# ---------------------------
# Follower Count Storage
# ---------------------------
def read_stored_followers(filepath: str) -> int:
    """Reads stored follower count; returns 0 if not found."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read().strip()
                return int(content.replace(",", "")) if content else 0
        except Exception as e:
            logger.error(f"Reading file error: {e}")
    return 0

def write_followers(filepath: str, count: int) -> None:
    """Writes follower count to file."""
    try:
        with open(filepath, "w") as f:
            f.write(str(count))
    except Exception as e:
        logger.error(f"Writing file error: {e}")

# ---------------------------
# Chrome Version Detection
# ---------------------------
CHROME_BINARY = "/usr/bin/google-chrome"  # Prefer Google Chrome over Chromium snap

def get_chrome_version() -> int:
    """Detects the installed Google Chrome major version."""
    try:
        result = subprocess.run([CHROME_BINARY, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Output: "Google Chrome 144.0.7559.109"
            version_str = result.stdout.strip().split()[-1]
            major_version = int(version_str.split('.')[0])
            logger.info(f"Detected Chrome version: {major_version}")
            return major_version
    except Exception as e:
        logger.warning(f"Could not detect Chrome version: {e}")
    
    # Fallback
    logger.warning("Using fallback Chrome version 144")
    return 144

# ---------------------------
# Selenium Setup for Blastup
# ---------------------------
def setup_blastup_driver() -> uc.Chrome:
    """Sets up undetected_chromedriver in headless mode and loads the blastup page."""
    options = uc.ChromeOptions()
    options.binary_location = CHROME_BINARY  # Force use of Google Chrome
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    try:
        # Dynamically detect Chrome version
        chrome_version = get_chrome_version()
        driver = uc.Chrome(version_main=chrome_version, options=options)
        driver.get(BLASTUP_URL)
        # Wait until the odometer element is present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "odometer")))
        logger.info("Blastup page loaded successfully.")
        return driver
    except Exception as e:
        logger.error(f"Error setting up blastup driver: {e}")
        raise

def fetch_follower_count_from_blastup(driver: uc.Chrome) -> Optional[int]:
    """
    Extracts the follower count from the blastup page.
    The follower count is displayed as separate digits within elements with the class 'odometer-value'.
    """
    try:
        # Locate all span elements containing individual digits
        digit_elements = driver.find_elements(By.CSS_SELECTOR, "span.odometer-value")
        if not digit_elements:
            logger.warning("No odometer digits found on page.")
            return None

        # Concatenate text from each span to form the full count
        count_str = "".join([digit.text for digit in digit_elements])
        if count_str:
            count = int(count_str.replace(",", ""))
            return count
        else:
            logger.warning("Empty follower count string extracted.")
            return None
    except Exception as e:
        logger.error(f"Error fetching follower count from blastup: {e}")
        return None

# ---------------------------
# Audio Helper Functions
# ---------------------------
def get_random_audio(folder_path: str, category_key: str, last_played_dict: dict) -> str:
    """
    Selects a random MP3 file from folder_path ensuring it's not the same as the last played file for this category.
    """
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
        if not files:
            raise FileNotFoundError(f"No MP3 files found in {folder_path}")

        # Exclude the last played file if possible
        if category_key in last_played_dict and last_played_dict[category_key] in files and len(files) > 1:
            files.remove(last_played_dict[category_key])
        selected = random.choice(files)
        last_played_dict[category_key] = selected  # update the last played for this category
        return os.path.join(folder_path, selected)
    except Exception as e:
        logger.error(f"Error selecting random audio from {folder_path}: {e}")
        raise

def play_audio(audio_path: str) -> None:
    """Plays the specified audio file if it exists."""
    if os.path.exists(audio_path):
        subprocess.run(["mpg123", audio_path],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    else:
        logger.warning(f"Audio file not found: {audio_path}")

def play_gain_audio(diff: int) -> None:
    """
    Selects and plays the appropriate gain audio file based on the number of followers gained.
    Uses specific audio directories for 1-10 follower gains, then checkpoints for larger gains.
    """
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

    folder_path = AUDIO_DIRS_GAIN.get(category)
    if folder_path:
        try:
            audio_file = get_random_audio(folder_path, str(category), last_played_gain)
            play_audio(audio_file)
        except Exception as e:
            logger.error(f"Error playing gain audio for category {category}: {e}")
    else:
        logger.warning(f"No audio directory mapped for gain category {category}.")

def play_loss_audio(diff: int) -> None:
    """
    Plays the appropriate loss audio file based on the number of followers lost.
    Only two categories exist: 1 and 2. If loss is greater than 2, no audio is played.
    """
    if diff not in (1, 2):
        logger.info("Loss audio only configured for 1 or 2 follower losses.")
        return
    folder_path = AUDIO_DIRS_LOSS.get(diff)
    if folder_path:
        try:
            audio_file = get_random_audio(folder_path, str(diff), last_played_loss)
            play_audio(audio_file)
        except Exception as e:
            logger.error(f"Error playing loss audio for loss {diff}: {e}")
    else:
        logger.warning(f"No audio directory mapped for loss category {diff}.")

# ---------------------------
# Notification Functions
# ---------------------------
def send_notification(message: str) -> None:
    """Sends a desktop notification."""
    subprocess.run(["notify-send", "Instagram Update", message])

# ---------------------------
# Main Function
# ---------------------------
def main() -> None:
    wait_for_internet()  # Ensure internet is available before starting.
    driver = setup_blastup_driver()

    stored_count = read_stored_followers(FOLLOWERS_FILE)
    if stored_count == 0:
        new_count = fetch_follower_count_from_blastup(driver)
        if new_count is not None:
            stored_count = new_count
            write_followers(FOLLOWERS_FILE, stored_count)
            logger.info(f"Initial followers: {stored_count}")
        else:
            logger.error("Failed to fetch initial follower count.")
            return
    else:
        logger.info(f"Stored followers: {stored_count}")

    while True:
        # --- Internet connectivity handling ---
        if not is_connected():
            logger.warning("Internet connection lost. Retrying every 10 seconds...")
            wait_for_internet()
            logger.info("Internet connection restored. Restarting browser instance.")
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error quitting browser: {e}")
            driver = setup_blastup_driver()

        try:
            new_count = fetch_follower_count_from_blastup(driver)
            if new_count is None:
                logger.warning("Failed to fetch follower count, refreshing blastup page...")
                driver.refresh()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "odometer")))
                time.sleep(RETRY_INTERVAL)
                continue

            # Sanity check for implausible values
            if new_count <= MIN_FOLLOWERS or new_count > MAX_FOLLOWERS:
                logger.warning(f"Ignoring implausible reading: {new_count}")
            elif new_count == stored_count:
                logger.info(f"No change in followers ({stored_count}).")
            else:
                diff = new_count - stored_count
                if diff > 0:
                    if diff > MAX_INCREASE_THRESHOLD:
                        logger.warning(f"Ignoring glitch increase: +{diff}")
                    else:
                        unit = "follower" if diff == 1 else "followers"
                        message = f"You got {diff} {unit}. Total: {new_count}"
                        logger.info(message)
                        send_notification(message)
                        play_gain_audio(diff)
                        stored_count = new_count
                        write_followers(FOLLOWERS_FILE, stored_count)
                elif diff < 0:
                    drop = abs(diff)
                    if drop > MAX_DROP_THRESHOLD:
                        logger.warning(f"Ignoring glitch drop: -{drop}")
                    else:
                        unit = "follower" if drop == 1 else "followers"
                        message = f"You lost {drop} {unit}. Total: {new_count}"
                        logger.info(message)
                        send_notification(message)
                        # Only play loss audio for 1 or 2 follower loss
                        if drop in (1, 2):
                            play_loss_audio(drop)
                        stored_count = new_count
                        write_followers(FOLLOWERS_FILE, stored_count)
        except Exception as e:
            logger.error(f"Error during follower count processing: {e}. Retrying after error...")
            try:
                driver.refresh()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "odometer")))
            except Exception as re:
                logger.error(f"Error refreshing blastup page: {re}")
            time.sleep(RETRY_INTERVAL)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
