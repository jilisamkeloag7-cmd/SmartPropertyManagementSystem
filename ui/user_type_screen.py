print(">>> user_type_screen.py V2 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QFrame, QGridLayout,
                                QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QLinearGradient, QBrush, QColor, QPalette
from ui import theme


ROLE_CARD_W = 220
ROLE_CARD_H = 140
ROLE_GAP = 20


class UserTypeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._build()

    def _build(self):
        # Gradient background matching Welcome screen
        self.setAutoFillBackground(True)
        pal = self.palette()
        grad = QLinearGradient(0, 0, 0, 1)
        grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QColor("#eff6ff"))
        grad.setColorAt(1.0, QColor("#f8fafc"))
        pal.setBrush(QPalette.Window, QBrush(grad))
        self.setPalette(pal)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scroll-safe wrapper
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        # ============================================================
        # HEADER
        # ============================================================
        title = QLabel("Who are you?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: {theme.FS_3XL}px; "
            f"font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        layout.addSpacing(theme.SP_2)

        subtitle = QLabel("Select your role to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"font-size: {theme.FS_LG}px; color: {theme.TEXT_MUTED};"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(theme.SP_10)

        # ============================================================
        # ROLE CARDS (centered 2x2 grid)
        # ============================================================
        cards_container = QWidget()
        cards_container.setStyleSheet("background: transparent;")
        cards_outer = QHBoxLayout(cards_container)
        cards_outer.setContentsMargins(0, 0, 0, 0)
        cards_outer.addStretch(1)

        grid = QGridLayout()
        grid.setSpacing(ROLE_GAP)
        grid.setContentsMargins(0, 0, 0, 0)

        roles = [
            ("👑", "Administrator",     theme.PRIMARY),
            ("📋", "Property Manager",  "#8b5cf6"),     # violet
            ("🏠", "Owner",             theme.SUCCESS),
            ("👤", "Tenant / User",     theme.INFO),
        ]

        for i, (icon, role, accent) in enumerate(roles):
            card = self._build_role_card(icon, role, accent)
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)

        cards_outer.addLayout(grid)
        cards_outer.addStretch(1)
        layout.addWidget(cards_container)

        layout.addSpacing(theme.SP_10)

        # ============================================================
        # BACK BUTTON
        # ============================================================
        back_row = QHBoxLayout()
        back_row.addStretch()

        btn_back = QPushButton("← Back to Welcome")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setFixedHeight(38)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                font-size: {theme.FS_BASE}px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                color: {theme.PRIMARY};
            }}
        """)
        btn_back.clicked.connect(self._go_back)
        back_row.addWidget(btn_back)
        back_row.addStretch()

        layout.addLayout(back_row)

    def _build_role_card(self, icon, role, accent_color):
        card = QPushButton()
        card.setFixedSize(ROLE_CARD_W, ROLE_CARD_H)
        card.setCursor(Qt.PointingHandCursor)

        # Build with a two-line label: icon on top, role below
        card.setText(f"{icon}\n{role}")
        card.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.BG_CARD};
                border: 2px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
                font-size: {theme.FS_MD}px;
                font-weight: 500;
                color: {theme.TEXT_MAIN};
                padding: 20px 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {theme.PRIMARY_SOFT};
                border-color: {accent_color};
                color: {accent_color};
            }}
            QPushButton:pressed {{
                background-color: {theme.PRIMARY_SOFT};
            }}
        """)
        # Bigger emoji via a separate style trick — Qt doesn't support mixed sizes
        # in one label, so we accept the compromise. The emoji still renders larger
        # than typical text because it's a wide glyph.
        card.clicked.connect(lambda checked, r=role: self._on_role_selected(r))
        return card

    def _on_role_selected(self, role):
        self.parent_window.show_login(role)

    def _go_back(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)