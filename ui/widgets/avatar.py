print(">>> avatar.py V1 <<<")

import os
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QBrush, QPen, QPainterPath
from ui import theme


# Palette for initials fallback — deterministic per user
_INITIAL_COLOURS = [
    "#3b82f6",  # blue
    "#8b5cf6",  # violet
    "#10b981",  # emerald
    "#f59e0b",  # amber
    "#ec4899",  # pink
    "#0ea5e9",  # sky
    "#ef4444",  # red
    "#14b8a6",  # teal
]


def _colour_for(seed: str) -> str:
    if not seed:
        return _INITIAL_COLOURS[0]
    return _INITIAL_COLOURS[sum(ord(c) for c in seed) % len(_INITIAL_COLOURS)]


def _initials(name: str) -> str:
    parts = (name or "?").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    if parts:
        return parts[0][:2].upper()
    return "?"


def make_avatar_pixmap(image_path: str | None, name: str,
                        size: int = 40) -> QPixmap:
    """Return a circular QPixmap — image if available, else initials on colour."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # Circular clip path
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    loaded = False
    if image_path and os.path.isfile(image_path):
        img = QPixmap(image_path)
        if not img.isNull():
            scaled = img.scaled(size, size,
                                Qt.KeepAspectRatioByExpanding,
                                Qt.SmoothTransformation)
            x = max(0, (scaled.width() - size) // 2)
            y = max(0, (scaled.height() - size) // 2)
            cropped = scaled.copy(x, y, size, size)
            painter.drawPixmap(0, 0, cropped)
            loaded = True

    if not loaded:
        colour = _colour_for(name)
        painter.setBrush(QBrush(QColor(colour)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)

        painter.setPen(QColor(theme.TEXT_WHITE))
        font = QFont()
        font.setPointSize(max(10, size // 3))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, size, size),
                         Qt.AlignCenter, _initials(name))

    painter.end()

    # Optional thin border
    bordered = QPixmap(size, size)
    bordered.fill(Qt.transparent)
    p2 = QPainter(bordered)
    p2.setRenderHint(QPainter.Antialiasing, True)
    p2.drawPixmap(0, 0, pix)
    p2.setPen(QPen(QColor(theme.BORDER), 1))
    p2.setBrush(Qt.NoBrush)
    p2.drawEllipse(1, 1, size - 2, size - 2)
    p2.end()

    return bordered


class AvatarLabel(QLabel):
    """A round avatar label that can be resized and updated."""

    def __init__(self, name: str = "", image_path: str | None = None,
                 size: int = 40, parent=None):
        super().__init__(parent)
        self._size = size
        self._name = name
        self._image_path = image_path
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.refresh()

    def set_avatar(self, name: str, image_path: str | None):
        self._name = name or ""
        self._image_path = image_path
        self.refresh()

    def refresh(self):
        pix = make_avatar_pixmap(self._image_path, self._name, self._size)
        self.setPixmap(pix)