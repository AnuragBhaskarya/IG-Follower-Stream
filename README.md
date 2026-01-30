# 📊 Instagram Follower Tracker

A real-time Instagram follower tracking system with **desktop notifications**, **audio alerts**, and **animated GIF displays**. Get instant alerts whenever you gain or lose followers!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-Desktop_Notifications-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

- 🔄 **Real-time Tracking** — Checks follower count every 1-2 seconds
- 🎉 **Desktop Notifications** — Beautiful overlay notifications with fade animations
- 🎵 **Audio Alerts** — Custom voice announcements for gains/losses
- 🎬 **Animated GIFs** — Random GIF selection from folders (no consecutive repeats!)
- 🎨 **Fully Customizable** — Fonts, sizes, positions, colors - all configurable
- 🔌 **Multiple APIs** — Support for InstaStatistics, Blastup, and Lightricks

---

## 📁 Project Structure

```
followers_tracker/
├── core/                   # Core modules
│   ├── config.py           # All configuration settings
│   ├── tracker.py          # Main tracking loop
│   ├── notification_streaming.py  # Desktop notifications
│   ├── audio.py            # Audio playback system
│   ├── storage.py          # Follower count persistence
│   ├── network.py          # Internet connectivity checks
│   └── logger.py           # Logging configuration
│
├── apis/                   # API implementations
│   ├── instastatistics.py  # InstaStatistics API (recommended)
│   ├── blastup.py          # Blastup API
│   └── lightricks.py       # Lightricks API
│
├── assets/                 # Visual assets
│   ├── gain/               # 📂 Put gain GIFs here (random selection)
│   ├── loss/               # 📂 Put loss GIFs here (random selection)
│   ├── gain.gif            # Fallback gain animation
│   ├── loss.gif            # Fallback loss animation
│   └── font.ttf/.otf       # Custom font (optional)
│
├── audio/                  # Audio files
│   ├── get.mp3             # Intro sound for gains
│   ├── lost.mp3            # Intro sound for losses
│   ├── gain/               # Voice announcements for gains
│   │   ├── 1/              # "You got 1 follower" audio files
│   │   ├── 2/              # "You got 2 followers" audio files
│   │   └── ...             # And so on...
│   └── lost/               # Voice announcements for losses
│       ├── 1/
│       └── 2/
│
├── run_instastatistics.py  # 🚀 Main entry point (recommended)
├── run_blastup.py          # Alternative: Blastup API
├── run_lightricks.py       # Alternative: Lightricks API
├── followers.txt           # Stored follower count
└── log.txt                 # Activity logs
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install PyQt5 requests
```

### 2. Configure Your Username 📝

**Crucial Step:** You must set the Instagram username you want to track!

Open `core/config.py` and change the value:

```python
INSTAGRAM_USERNAME = "ishowspeed"  # <--- Replace with your target username
```

### 3. Run the Tracker

```bash
python3 run_instastatistics.py
```

---

## ⚙️ Configuration

All settings are in `core/config.py`:

### Tracker Settings

```python
CHECK_INTERVAL = 1        # Seconds between API checks
RETRY_INTERVAL = 5        # Seconds to wait on error
AUDIO_OVERLAY_DELAY = 1   # Delay before voice plays after intro
```

### Notification Appearance

```python
# GIF/Image sizes (height in pixels, width scales automatically)
GAIN_GIF_SIZE = 150
LOSS_GIF_SIZE = 150

# Position from screen edges
NOTIF_RIGHT_OFFSET = -20  # Negative = closer to edge
NOTIF_TOP_OFFSET = 0      # 0 = top of screen

# Timing
NOTIFICATION_COOLDOWN = 5  # Prevents overlapping notifications
```

### Font Settings

```python
NOTIF_FONT_FAMILY = "Arial Black"  # Or use custom font.ttf in assets/
NOTIF_LINE1_SIZE = 20              # Main text size
NOTIF_LINE2_SIZE = 18              # "Total: X" text size
NOTIF_LINE_SPACING = 1             # Line spacing (lower = tighter)
```

---

## 🎨 Customization

### Adding Custom GIFs

1. **Create folders** (if not already present):
   ```bash
   mkdir -p assets/gain assets/loss
   ```

2. **Add your GIFs**:
   ```
   assets/gain/celebrate.gif
   assets/gain/party.gif
   assets/loss/sad.gif
   assets/loss/cry.gif
   ```

3. **That's it!** — GIFs are selected randomly, and won't repeat consecutively.

### Custom Fonts

1. Download any `.ttf` or `.otf` font
2. Rename it to `font.ttf` or `font.otf`
3. Place it in the `assets/` folder
4. The notification will use it automatically!

### Audio Customization

Add `.mp3` files to the appropriate folders:

```
audio/gain/1/   → Random audio for gaining 1 follower
audio/gain/2/   → Random audio for gaining 2 followers
audio/gain/more_than_10/  → For gains of 11+
audio/gain/more_than_100/ → For gains of 100+
```

---

## 🔌 API Options

### InstaStatistics (Recommended)
```bash
python3 run_instastatistics.py
```
- ✅ Fast (2-second cache)
- ✅ Reliable
- ✅ No authentication needed

### Blastup
```bash
python3 run_blastup.py
```

### Lightricks
```bash
python3 run_lightricks.py
```

---

## 📝 How It Works

1. **Fetch** — Calls the API to get current follower count
2. **Compare** — Checks against stored count in `followers.txt`
3. **Notify** — If changed, shows desktop notification with GIF
4. **Audio** — Plays intro sound + random voice announcement
5. **Store** — Saves new count and waits for next check

---

## 🛡️ Built-in Protection

- **Network checks** — Waits for internet if disconnected
- **Notification cooldown** — Prevents overlapping alerts
- **No artificial limits** — Works for any follower count (1 to millions!)

---

## 📋 Requirements

- Python 3.8+
- PyQt5
- requests
- mpv (for audio playback)

---

## 🤝 Contributing

Feel free to submit issues and pull requests!

---

## 📄 License

MIT License - Feel free to use and modify!

---

Made with ❤️ for content creators who want to celebrate every new follower! 🎉
