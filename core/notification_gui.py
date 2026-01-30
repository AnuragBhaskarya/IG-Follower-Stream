"""
Graphical notification system with animated GIF and fade effects.
Uses PyQt5 for a premium notification experience.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QMovie, QFont, QColor, QPalette

from .config import PROJECT_DIR
from .logger import logger

# Image paths
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
IMG_GAIN = os.path.join(ASSETS_DIR, "gain.png")
IMG_LOSS = os.path.join(ASSETS_DIR, "loss.gif")

# Notification settings
NOTIFICATION_DURATION = 4000  # ms to show notification
FADE_DURATION = 500  # ms for fade in/out


class AnimatedNotification(QWidget):
    """A beautiful animated notification with GIF and fade effects."""
    
    def __init__(self, message: str, is_gain: bool = True):
        # Create app if needed (for standalone use)
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        super().__init__()
        self.message = message
        self.is_gain = is_gain
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Configure the notification window."""
        # Window properties
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Main container with rounded corners and gradient
        self.container = QWidget(self)
        if self.is_gain:
            self.container.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(34, 197, 94, 240),
                        stop:1 rgba(22, 163, 74, 240));
                    border-radius: 16px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }
            """)
        else:
            self.container.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(239, 68, 68, 240),
                        stop:1 rgba(220, 38, 38, 240));
                    border-radius: 16px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }
            """)
        
        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(20, 15, 20, 15)
        container_layout.setSpacing(15)
        
        # Image label
        self.img_label = QLabel()
        img_path = IMG_GAIN if self.is_gain else IMG_LOSS
        if os.path.exists(img_path):
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap(img_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_label.setPixmap(pixmap)
        else:
            # Fallback emoji
            self.img_label.setText("📈" if self.is_gain else "📉")
            self.img_label.setStyleSheet("font-size: 40px;")
        
        container_layout.addWidget(self.img_label)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        # Title
        title = QLabel("Follower Gained! 🎉" if self.is_gain else "Follower Lost 😢")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        text_layout.addWidget(title)
        
        # Message
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)
        msg_label.setWordWrap(True)
        text_layout.addWidget(msg_label)
        
        container_layout.addLayout(text_layout)
        container_layout.addStretch()
        
        # Size and position
        self.setFixedSize(380, 100)
        self.position_notification()
        
        # Opacity effect for fade
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
    
    def position_notification(self):
        """Position at top-right corner of screen."""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = 40
        self.move(x, y)
    
    def setup_animations(self):
        """Setup fade in and fade out animations."""
        # Fade in
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(FADE_DURATION)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade out
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(FADE_DURATION)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.close)
        
        # Timer to start fade out
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.start_fade_out)
    
    def show_notification(self):
        """Show the notification with fade-in effect."""
        self.show()
        self.fade_in.start()
        self.close_timer.start(NOTIFICATION_DURATION)
    
    def start_fade_out(self):
        """Start the fade-out animation."""
        self.fade_out.start()
    
    def run(self):
        """Run the notification (blocking for standalone, non-blocking for integrated)."""
        self.show_notification()
        # Process events briefly to show notification
        for _ in range(50):
            self.app.processEvents()
            import time
            time.sleep(0.01)


def show_graphical_notification(message: str, is_gain: bool = True) -> None:
    """
    Shows a beautiful animated notification.
    Non-blocking - runs in its own process.
    """
    import subprocess
    import json
    
    # Run in separate process to avoid blocking
    script = f'''
import sys
sys.path.insert(0, "{PROJECT_DIR}")
from core.notification_gui import AnimatedNotification
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import time

app = QApplication(sys.argv)
notif = AnimatedNotification("{message}", {is_gain})
notif.show_notification()

# Auto-close after notification duration + fade
QTimer.singleShot({NOTIFICATION_DURATION + FADE_DURATION + 100}, app.quit)
app.exec_()
'''
    
    try:
        subprocess.Popen(
            ["python3", "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Graphical notification error: {e}")
        # Fallback to basic notification
        subprocess.run(["notify-send", "Instagram Followers", message])
