print(">>> welcome_screen.py V2 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QLinearGradient, QBrush, QColor, QPalette
from ui import theme


class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._build()

    def _build(self):
        # Gradient background on the whole widget
        self.setAutoFillBackground(True)
        pal = self.palette()
        grad = QLinearGradient(0, 0, 0, 1)
        grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QColor("#eff6ff"))
        grad.setColorAt(1.0, QColor("#f8fafc"))
        pal.setBrush(QPalette.Window, QBrush(grad))
        self.setPalette(pal)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)
        layout.setContentsMargins(40, 40, 40, 40)

        # ---- Logo mark
        logo = QLabel("🏢")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 72px;")
        layout.addWidget(logo)

        layout.addSpacing(theme.SP_4)

        # ---- Title
        title = QLabel("Smart Property Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: {theme.FS_3XL}px; "
            f"font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        layout.addSpacing(theme.SP_2)

        # ---- Subtitle
        subtitle = QLabel("Streamline your property operations with ease")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: {theme.FS_LG}px; "
            f"color: {theme.TEXT_MUTED};"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(theme.SP_10)

        # ---- CTA card (thin container for the button)
        btn = QPushButton("Get Started")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(240, 56)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PRIMARY};
                color: {theme.TEXT_WHITE};
                border: none;
                border-radius: {theme.RADIUS_PILL}px;
                font-size: {theme.FS_LG}px;
                font-weight: bold;
                padding: 0 30px;
            }}
            QPushButton:hover    {{ background-color: {theme.PRIMARY_HOVER}; }}
            QPushButton:pressed  {{ background-color: {theme.PRIMARY_PRESSED}; }}
        """)
        btn.clicked.connect(self._on_start)

        # Centre the button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addSpacing(theme.SP_10)

        # ---- Footer hint
        hint = QLabel("Version 0.1  •  ENEL2SEH1 Group Project")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(
            f"font-size: {theme.FS_XS}px; color: {theme.TEXT_FAINT};"
        )
        layout.addWidget(hint)

    def _on_start(self):
        self.parent_window.show_user_type()