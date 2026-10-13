
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from ui import theme


class LoadingOverlay(QWidget):
    """
    Semi-transparent overlay with a spinning indicator.
    Attach to any QWidget screen using:
        self._overlay = LoadingOverlay(self, "Loading…")
        self._overlay.show_loading()
        self._overlay.hide_loading()
    """

    def __init__(self, parent: QWidget, message: str = "Loading…"):
        super().__init__(parent)
        _f = self.font()
        if _f.pointSize() <= 0:
            _f.setPointSize(10)
            self.setFont(_f)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("""
            LoadingOverlay { background: rgba(23, 11, 41, 180); }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)

        self._spin_label = QLabel("◐")
        self._spin_label.setAlignment(Qt.AlignCenter)
        self._spin_label.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: 40px; background: transparent;"
        )
        layout.addWidget(self._spin_label, alignment=Qt.AlignCenter)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: {theme.FS_MD}px; "
            f"font-weight: bold; background: transparent;"
        )
        layout.addWidget(self.label)

        self.hide()

        self._spin_chars = ["◐", "◓", "◑", "◒"]
        self._spin_index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _tick(self):
        self._spin_index = (self._spin_index + 1) % len(self._spin_chars)
        self._spin_label.setText(self._spin_chars[self._spin_index])

    def show_loading(self, message: str | None = None):
        if message:
            self.label.setText(message)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()
        self._timer.start(80)

    def hide_loading(self):
        self._timer.stop()
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
