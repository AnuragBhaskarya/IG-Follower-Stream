"""
Audio playback system with overlay support.
Plays intro jingle, then voice announcement after delay.
"""

import os
import subprocess
import random
import time
import threading
from typing import Dict

from .config import (
    AUDIO_GET, AUDIO_LOST, AUDIO_DIRS_GAIN, AUDIO_DIRS_LOSS,
    AUDIO_OVERLAY_DELAY
)
from .logger import logger

# Track last played file to avoid repetition
last_played_gain: Dict[str, str] = {}
last_played_loss: Dict[str, str] = {}


def get_random_audio(folder_path: str, category_key: str, last_played_dict: dict) -> str:
    """Selects a random MP3 file from folder, avoiding last played."""
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
    """Plays an audio file using mpv (non-blocking)."""
    if audio_path and os.path.exists(audio_path):
        subprocess.Popen(["mpv", "--no-terminal", audio_path])
    else:
        logger.warning(f"Audio file not found: {audio_path}")


def play_audio_with_overlay(intro_path: str, voice_path: str, delay: float = AUDIO_OVERLAY_DELAY) -> None:
    """
    Plays intro audio, then overlays voice after delay.
    The voice starts playing while intro may still be going.
    """
    def delayed_voice():
        time.sleep(delay)
        if voice_path and os.path.exists(voice_path):
            subprocess.Popen(["mpv", "--no-terminal", "--no-video", voice_path])
    
    # Start intro immediately
    if intro_path and os.path.exists(intro_path):
        subprocess.Popen(["mpv", "--no-terminal", "--no-video", intro_path])
    
    # Start voice after delay in separate thread
    if voice_path:
        threading.Thread(target=delayed_voice, daemon=True).start()


def get_gain_category(diff: int):
    """Determines the audio category based on follower gain amount."""
    if diff <= 10:
        return diff
    elif diff <= 100:
        return "more_than_10"
    elif diff <= 500:
        return "more_than_100"
    elif diff <= 1000:
        return "more_than_500"
    elif diff <= 2000:
        return "more_than_1000"
    elif diff <= 5000:
        return "more_than_2000"
    else:
        return "more_than_5000"


def play_gain_audio(diff: int) -> None:
    """Plays gain audio with get.mp3 intro overlay."""
    category = get_gain_category(diff)
    
    if category in AUDIO_DIRS_GAIN:
        folder = AUDIO_DIRS_GAIN[category]
        voice_audio = get_random_audio(folder, str(category), last_played_gain)
        play_audio_with_overlay(AUDIO_GET, voice_audio)


def play_loss_audio(diff: int) -> None:
    """Plays loss audio with lost.mp3 intro overlay."""
    # Get voice audio if available for 1-2 losses
    voice_audio = ""
    if diff in AUDIO_DIRS_LOSS:
        folder = AUDIO_DIRS_LOSS[diff]
        voice_audio = get_random_audio(folder, str(diff), last_played_loss)
    
    # Always play intro, with or without voice
    play_audio_with_overlay(AUDIO_LOST, voice_audio)

