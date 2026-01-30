"""
Streaming-style notification overlay with thick black text strokes.
"""

import os
import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QRectF
from PyQt5.QtGui import (
    QMovie, QFont, QColor, QPainter, QPixmap, 
    QPen, QBrush, QPainterPath, QFontMetrics
)

from .config import (
    PROJECT_DIR, GAIN_GIF_SIZE, GAIN_PNG_SIZE, LOSS_GIF_SIZE, LOSS_PNG_SIZE,
    NOTIF_RIGHT_OFFSET, NOTIF_TOP_OFFSET,
    NOTIF_LINE1_SIZE, NOTIF_LINE2_SIZE, NOTIF_LINE_SPACING
)
from .logger import logger
import random
import glob

# Asset paths
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")

# GIF folders (put multiple .gif files here for random selection)
GIF_GAIN_DIR = os.path.join(ASSETS_DIR, "gain")
GIF_LOSS_DIR = os.path.join(ASSETS_DIR, "loss")

# Single file fallbacks (if folders are empty)
GIF_GAIN_FALLBACK = os.path.join(ASSETS_DIR, "gain.gif")
GIF_LOSS_FALLBACK = os.path.join(ASSETS_DIR, "loss.gif")
IMG_GAIN_FALLBACK = os.path.join(ASSETS_DIR, "gain.png")
IMG_LOSS_FALLBACK = os.path.join(ASSETS_DIR, "loss.png")

# Custom font (put font.ttf or font.otf in assets folder)
FALLBACK_FONT = "Arial Black"  # System font fallback

# Track last used GIFs to avoid consecutive repeats
_last_gain_gif = None
_last_loss_gif = None

def get_random_gif(is_gain: bool) -> str:
    """Get a random GIF from the gain/loss folder, avoiding consecutive repeats."""
    global _last_gain_gif, _last_loss_gif
    
    folder = GIF_GAIN_DIR if is_gain else GIF_LOSS_DIR
    last_used = _last_gain_gif if is_gain else _last_loss_gif
    
    # Look for GIFs in folder
    if os.path.isdir(folder):
        gifs = glob.glob(os.path.join(folder, "*.gif"))
        if gifs:
            # Filter out last used if we have more than 1 option
            if len(gifs) > 1 and last_used in gifs:
                gifs = [g for g in gifs if g != last_used]
            
            chosen = random.choice(gifs)
            
            # Update last used
            if is_gain:
                _last_gain_gif = chosen
            else:
                _last_loss_gif = chosen
            
            return chosen
    
    # Fallback to single files
    single_gif = GIF_GAIN_FALLBACK if is_gain else GIF_LOSS_FALLBACK
    if os.path.exists(single_gif):
        return single_gif
    
    single_png = IMG_GAIN_FALLBACK if is_gain else IMG_LOSS_FALLBACK
    if os.path.exists(single_png):
        return single_png
    
    return ""  # No asset found

# Notification settings
NOTIFICATION_DURATION = 5000
FADE_DURATION = 400

# Colors
GREEN = QColor(76, 175, 80)
RED = QColor(244, 67, 54)
WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)

# Load custom font if exists
from PyQt5.QtGui import QFontDatabase
_font_id = -1
_custom_font_name = None

# Supported font files (in order of preference)
FONT_FILES = [
    os.path.join(ASSETS_DIR, "font.ttf"),
    os.path.join(ASSETS_DIR, "font.otf"),
]

def get_font_family():
    """Load custom font from assets or fallback to system font."""
    global _font_id, _custom_font_name
    
    if _custom_font_name:
        return _custom_font_name
    
    # Try each font file
    for font_file in FONT_FILES:
        if os.path.exists(font_file):
            _font_id = QFontDatabase.addApplicationFont(font_file)
            if _font_id >= 0:
                families = QFontDatabase.applicationFontFamilies(_font_id)
                if families:
                    _custom_font_name = families[0]
                    logger.info(f"Loaded custom font: {_custom_font_name}")
                    return _custom_font_name
    
    logger.info(f"Using fallback font: {FALLBACK_FONT}")
    return FALLBACK_FONT


class StrokedTextLabel(QWidget):
    """Custom widget that draws text with thick black stroke."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []  # List of (text, color) tuples
        self.font = QFont(get_font_family(), 20, QFont.Black)
        self.stroke_width = 4
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def set_text_segments(self, segments):
        """Set text as list of (text, QColor) tuples."""
        self.segments = segments
        self.update()
        self.adjustSize()
    
    def set_font_size(self, size):
        self.font.setPointSize(size)
        self.update()
    
    def sizeHint(self):
        fm = QFontMetrics(self.font)
        total_text = "".join([s[0] for s in self.segments])
        width = fm.horizontalAdvance(total_text) + self.stroke_width * 4
        height = fm.height() + self.stroke_width * 4
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        fm = QFontMetrics(self.font)
        total_text = "".join([s[0] for s in self.segments])
        width = fm.horizontalAdvance(total_text) + self.stroke_width * 4
        height = fm.height() + self.stroke_width * 4
        from PyQt5.QtCore import QSize
        return QSize(max(width, 350), max(height, 30))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(self.font)
        
        fm = QFontMetrics(self.font)
        
        # Calculate total width for centering
        total_width = sum(fm.horizontalAdvance(seg[0]) for seg in self.segments)
        x_start = (self.width() - total_width) / 2
        y = self.height() / 2 + fm.ascent() / 2 - fm.descent() / 2
        
        current_x = x_start
        
        for text, color in self.segments:
            # Create path for this segment
            path = QPainterPath()
            path.addText(current_x, y, self.font, text)
            
            # Draw thick black stroke
            stroke_pen = QPen(BLACK, self.stroke_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.strokePath(path, stroke_pen)
            
            # Fill with color
            painter.fillPath(path, QBrush(color))
            
            current_x += fm.horizontalAdvance(text)


class StreamingNotification(QWidget):
    """Streaming-style transparent notification with stroked text."""
    
    def __init__(self, line1_segments, line2_segments, is_gain: bool = True, gif_path: str = None):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        super().__init__()
        self.line1_segments = line1_segments
        self.line2_segments = line2_segments
        self.is_gain = is_gain
        self.gif_path = gif_path
        self.movie = None
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet("background: transparent;")
        
        # Vertical layout - image TOP, text BELOW
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 0, 10)  # left, top, right, bottom
        layout.setSpacing(NOTIF_LINE_SPACING)
        layout.setAlignment(Qt.AlignCenter)
        
        # Character image - TOP
        self.char_label = QLabel()
        self.char_label.setAlignment(Qt.AlignCenter)
        self.char_label.setStyleSheet("background: transparent;")
        
        # Use provided path or fallback (though path should be provided by caller now)
        gif_path = self.gif_path if self.gif_path else get_random_gif(self.is_gain)
        
        if gif_path and gif_path.endswith('.gif'):
            self.movie = QMovie(gif_path)
            target_height = GAIN_GIF_SIZE if self.is_gain else LOSS_GIF_SIZE
            
            # Get original size and calculate scaled width to preserve aspect ratio
            self.movie.jumpToFrame(0)
            original_size = self.movie.currentImage().size()
            if original_size.height() > 0:
                aspect_ratio = original_size.width() / original_size.height()
                scaled_width = int(target_height * aspect_ratio)
            else:
                scaled_width = target_height
            
            self.current_img_size = target_height
            self.movie.setScaledSize(QSize(scaled_width, target_height))
            self.char_label.setMovie(self.movie)
            self.movie.start()
        elif gif_path and gif_path.endswith('.png'):
            png_size = GAIN_PNG_SIZE if self.is_gain else LOSS_PNG_SIZE
            self.current_img_size = png_size
            pixmap = QPixmap(gif_path).scaled(png_size, png_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.char_label.setPixmap(pixmap)
        else:
            self.char_label.setText("🎉" if self.is_gain else "😢")
            self.char_label.setStyleSheet("font-size: 60px; background: transparent;")
            self.current_img_size = 80
        
        layout.addWidget(self.char_label, alignment=Qt.AlignCenter)
        
        # Line 1 - stroked text
        self.line1_widget = StrokedTextLabel()
        self.line1_widget.set_font_size(NOTIF_LINE1_SIZE)
        self.line1_widget.set_text_segments(self.line1_segments)
        self.line1_widget.setFixedHeight(40)
        layout.addWidget(self.line1_widget, alignment=Qt.AlignCenter)
        
        # Line 2 - stroked text
        self.line2_widget = StrokedTextLabel()
        self.line2_widget.set_font_size(NOTIF_LINE2_SIZE)
        self.line2_widget.set_text_segments(self.line2_segments)
        self.line2_widget.setFixedHeight(35)
        layout.addWidget(self.line2_widget, alignment=Qt.AlignCenter)
        
        # Dynamic size based on image size
        # Width: at least 400, or image size + padding
        # Height: image + text lines + padding
        img_size = getattr(self, 'current_img_size', 100)
        window_width = max(400, img_size + 100)
        window_height = img_size + 40 + 35 + 80  # image + line1 + line2 + padding
        
        self.setFixedSize(window_width, window_height)
        self.position_notification()
        self.setWindowOpacity(0)
    
    def position_notification(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - NOTIF_RIGHT_OFFSET
        y = NOTIF_TOP_OFFSET
        self.move(x, y)
    
    def setup_animations(self):
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(FADE_DURATION)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(FADE_DURATION)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.close)
        
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.fade_out.start)
    
    def show_notification(self):
        self.show()
        self.fade_in.start()
        self.close_timer.start(NOTIFICATION_DURATION)


def show_streaming_notification(message: str, is_gain: bool = True, gif_path: str = None) -> None:
    """Shows streaming-style notification with stroked text."""
    import subprocess
    import json
    
    color = "GREEN" if is_gain else "RED"
    
    # Parse: "You got X followers. Total: Y"
    match = re.match(r"You (got|lost) (\d+) (followers?)\. Total: (\d+)", message)
    
    if match:
        verb = match.group(1)
        count = match.group(2)
        unit = match.group(3)
        total = match.group(4)
        
        # Build segments for line 1
        line1_data = [
            ("You ", "WHITE"),
            (f"{verb} {count}", color),
            (f" {unit}", "WHITE")
        ]
        
        # Build segments for line 2
        line2_data = [
            ("Total: ", "WHITE"),
            (total, color)
        ]
    else:
        line1_data = [(message, "WHITE")]
        line2_data = []
    
    script = f'''
import sys
sys.path.insert(0, "{PROJECT_DIR}")
from core.notification_streaming import StreamingNotification, GREEN, RED, WHITE
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

color_map = {{"GREEN": GREEN, "RED": RED, "WHITE": WHITE}}

line1 = {line1_data}
line2 = {line2_data}

line1_segments = [(t, color_map[c]) for t, c in line1]
line2_segments = [(t, color_map[c]) for t, c in line2]

app = QApplication(sys.argv)
notif = StreamingNotification(line1_segments, line2_segments, {is_gain}, "{gif_path}")
notif.show_notification()

# Connect to closed signal to quit app
notif.destroyed.connect(app.quit)

# Fallback quit timer (in case close doesn't trigger)
QTimer.singleShot({NOTIFICATION_DURATION + FADE_DURATION + 500}, app.quit)
app.exec_()
'''
    
    try:
        subprocess.Popen(
            ["python3", "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Streaming notification error: {e}")
        subprocess.run(["notify-send", "Instagram Followers", message])
