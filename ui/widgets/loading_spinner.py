print(">>> loading_spinner.py V1 <<<")

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen
from ui import theme


class LoadingSpinner(QWidget):
    """A simple rotating arc spinner. Call start() / stop() to animate."""

    def __init__(self, size: int = 40, colour: str | None = None, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._size = size
        self._colour = QColor(colour or theme.PRIMARY)
        self.setFixedSize(size, size)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.show()
        self._timer.start(60)   # ~16 fps

    def stop(self):
        self._timer.stop()
        self.hide()

    def _tick(self):
        self._angle = (self._angle + 20) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self._colour)
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        margin = 4
        rect = QRect(margin, margin,
                     self._size - 2 * margin, self._size - 2 * margin)
        # 270° arc, rotating
        painter.drawArc(rect, self._angle * 16, 270 * 16)


class LoadingOverlay(QWidget):
    """
    A full-widget overlay that shows a spinner and blocks clicks
    while a background operation completes.
    """

    def __init__(self, parent: QWidget, message: str = "Loading…"):
        super().__init__(parent)
        self.setStyleSheet(f"""
            LoadingOverlay {{
                background: rgba(15, 23, 42, 120);
            }}
        """)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        self.spinner = LoadingSpinner(size=44,
                                      colour=theme.TEXT_WHITE,
                                      parent=self)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: {theme.FS_MD}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(self.label)

    def show_loading(self, message: str | None = None):
        if message:
            self.label.setText(message)
        if self.parent():
            self.resize(self.parent().size())
        self.raise_()
        self.show()
        self.spinner.start()

    def hide_loading(self):
        self.spinner.stop()
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())