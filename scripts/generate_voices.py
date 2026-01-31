#!/usr/bin/env python3
"""
Generate voice files for Follower Tracker using Pocket TTS.
Generates:
- Gains: 1 to 10,000
- Losses: 1 to 100
- "Over" messages
"""

import os
import sys
import soundfile as sf
from pocket_tts import TTSModel
import torch
import argparse

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "generated")
GAIN_DIR = os.path.join(AUDIO_DIR, "gain")
LOSS_DIR = os.path.join(AUDIO_DIR, "loss")

import concurrent.futures
import math
# import multiprocessing # Not used for sequential
from tqdm import tqdm
from num2words import num2words

# Selected voice from catalog: "alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"
SELECTED_VOICE = "alba"

def setup_dirs():
    os.makedirs(GAIN_DIR, exist_ok=True)
    os.makedirs(LOSS_DIR, exist_ok=True)

def generate_milestones(model, speaker_state):
    """Generate the 'over X' messages and milestones"""
    
    # 1. Gain Milestones: 100 to 1000 (step 100)
    for i in range(100, 1000, 100):
        filename = os.path.join(GAIN_DIR, f"more_than_{i}.wav")
        if not os.path.exists(filename):
            num_text = num2words(i)
            text = f"You got more than {num_text} followers"
            print(f"Generating milestone: {text}")
            audio = model.generate_audio(speaker_state, text)
            sf.write(filename, audio.squeeze().cpu().numpy(), 24000)

    # 2. Gain Milestones: 1000 to 10000 (step 1000)
    for i in range(1000, 11000, 1000):
        filename = os.path.join(GAIN_DIR, f"more_than_{i}.wav")
        if not os.path.exists(filename):
            num_text = num2words(i)
            text = f"You got more than {num_text} followers"
            print(f"Generating milestone: {text}")
            audio = model.generate_audio(speaker_state, text)
            sf.write(filename, audio.squeeze().cpu().numpy(), 24000)

    # Loss Over Limit (100)
    filename = os.path.join(LOSS_DIR, "over_100.wav")
    if not os.path.exists(filename):
        text = "You lost more than one hundred followers"
        audio = model.generate_audio(speaker_state, text)
        sf.write(filename, audio.squeeze().cpu().numpy(), 24000)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Generate only first 5 files for testing")
    parser.add_argument("--limit-gain", type=int, default=100, help="Generate specific files up to this number (default 100)")
    parser.add_argument("--limit-loss", type=int, default=100)
    parser.add_argument("--voice", type=str, default=SELECTED_VOICE, help="Voice name from catalog")
    args = parser.parse_args()

    setup_dirs()
    
    print("Loading Pocket TTS Model...")
    model = TTSModel.load_model()
    
    print(f"Conditioning on voice: {args.voice}...")
    try:
        speaker_state = model.get_state_for_audio_prompt(args.voice)
    except Exception as e:
        print(f"Error loading voice '{args.voice}': {e}")
        print("Falling back to 'marius'...")
        speaker_state = model.get_state_for_audio_prompt("marius")

    if args.test:
        print("TEST MODE: Generating 5 files each.")
        gain_limit = 5
        loss_limit = 5
    else:
        gain_limit = args.limit_gain
        loss_limit = args.limit_loss

    print(f"Generating specific gains 1-{gain_limit}, and tiered milestones.")

    total_tasks = gain_limit + loss_limit
    
    with tqdm(total=total_tasks, unit="file") as pbar:
        # 1. Gains (Specific)
        pbar.set_description("Gains")
        for i in range(1, gain_limit + 1):
            filename = os.path.join(GAIN_DIR, f"{i}.wav")
            pbar.update(1)
            
            if os.path.exists(filename):
                continue

            num_text = num2words(i)
            text = f"You got {num_text} follower" if i == 1 else f"You got {num_text} followers"
            
            try:
                audio = model.generate_audio(speaker_state, text)
                sf.write(filename, audio.squeeze().cpu().numpy(), 24000)
            except Exception as e:
                tqdm.write(f"Error generating {i}: {e}")

        # 2. Losses (Specific)
        pbar.set_description("Losses")
        for i in range(1, loss_limit + 1):
            filename = os.path.join(LOSS_DIR, f"{i}.wav")
            pbar.update(1)
            
            if os.path.exists(filename):
                continue

            num_text = num2words(i)
            text = f"You lost {num_text} follower" if i == 1 else f"You lost {num_text} followers"
            
            try:
                audio = model.generate_audio(speaker_state, text)
                sf.write(filename, audio.squeeze().cpu().numpy(), 24000)
            except Exception as e:
                tqdm.write(f"Error generating loss {i}: {e}")

    print("Generating milestones...")
    generate_milestones(model, speaker_state)
    print("All done!")

if __name__ == "__main__":
    main()
