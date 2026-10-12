print(">>> connection_banner.py V1 <<<")

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer
from Services.connectivity_service import is_online
from Database.config import IS_CLOUD
from ui import theme


class ConnectionBanner(QFrame):
    """Red banner shown at the top of the app when offline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.DANGER};
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(14)

        icon = QLabel("⚠")
        icon.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: 20px;"
        )
        layout.addWidget(icon)

        self.message = QLabel(
            "You appear to be offline. The app cannot reach the server."
        )
        self.message.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: {theme.FS_BASE}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(self.message, stretch=1)

        self.btn_retry = QPushButton("Retry")
        self.btn_retry.setCursor(Qt.PointingHandCursor)
        self.btn_retry.setFixedSize(80, 30)
        self.btn_retry.setStyleSheet(f"""
            QPushButton {{
                background: {theme.TEXT_WHITE};
                color: {theme.DANGER};
                border: none;
                border-radius: {theme.RADIUS_MD}px;
                font-weight: bold;
                font-size: {theme.FS_BASE}px;
            }}
            QPushButton:hover {{ background: #f1f5f9; }}
        """)
        self.btn_retry.clicked.connect(self._on_retry)
        layout.addWidget(self.btn_retry)

        self.setVisible(False)

        # Only poll in cloud mode
        if IS_CLOUD:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._auto_check)
            self._timer.start(5000)   # every 5 seconds
            QTimer.singleShot(1500, self._auto_check)   # initial check

    def _auto_check(self):
        if is_online():
            self.setVisible(False)
        else:
            self.message.setText(
                "You appear to be offline. The app cannot reach the server."
            )
            self.setVisible(True)

    def _on_retry(self):
        self.message.setText("Checking connection…")
        self.btn_retry.setEnabled(False)
        QTimer.singleShot(200, self._retry_check)

    def _retry_check(self):
        self.btn_retry.setEnabled(True)
        if is_online():
            self.setVisible(False)
        else:
            self.message.setText(
                "Still offline. Please check your internet connection."
            )