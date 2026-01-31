"""
Audio playback system with overlay support.
Plays intro jingle, then voice announcement after delay.
"""

import os
import subprocess
import time
import threading

from .config import (
    AUDIO_GET, AUDIO_LOST, GENERATED_AUDIO_DIR,
    AUDIO_OVERLAY_DELAY
)
from .logger import logger


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


def play_gain_audio(diff: int) -> None:
    """Plays gain audio with get.mp3 intro overlay."""
    voice_file = ""
    
    if diff <= 100:
        # Specific file 1-100
        path = os.path.join(GENERATED_AUDIO_DIR, "gain", f"{diff}.wav")
        if os.path.exists(path):
            voice_file = path
    elif diff <= 1000:
        # Milestones 100-1000 (step 100)
        milestone = (diff // 100) * 100
        path = os.path.join(GENERATED_AUDIO_DIR, "gain", f"more_than_{milestone}.wav")
        if os.path.exists(path):
            voice_file = path
    else:
        # Milestones 1000-10000 (step 1000)
        milestone = (diff // 1000) * 1000
        if milestone > 10000:
            milestone = 10000
        path = os.path.join(GENERATED_AUDIO_DIR, "gain", f"more_than_{milestone}.wav")
        if os.path.exists(path):
            voice_file = path
    
    # Play intro with overlay
    play_audio_with_overlay(AUDIO_GET, voice_file)


def play_loss_audio(diff: int) -> None:
    """Plays loss audio with lost.mp3 intro overlay."""
    voice_file = ""
    
    # Check for specific number file
    specific_file = os.path.join(GENERATED_AUDIO_DIR, "loss", f"{diff}.wav")
    over_file = os.path.join(GENERATED_AUDIO_DIR, "loss", "over_100.wav")
    
    if os.path.exists(specific_file):
        voice_file = specific_file
    elif diff > 100 and os.path.exists(over_file):
        voice_file = over_file
    
    # Always play intro, with or without voice
    play_audio_with_overlay(AUDIO_LOST, voice_file)

