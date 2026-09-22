print(">>> property_detail_dialog.py V1 <<<")

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from Controllers.property_controller import PropertyController
from ui import theme


IMAGE_W = 620
IMAGE_H = 340


class PropertyDetailDialog(QDialog):
    """Rich detail view of a property with image gallery navigation."""

    def __init__(self, parent=None, property_data: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.controller = PropertyController()
        self.images = []
        self.current_index = 0

        pid = self.property_data.get("property_id")
        if pid:
            try:
                self.images = self.controller.list_images(pid)
            except Exception:
                self.images = []

        self.setWindowTitle(self.property_data.get("address", "Property"))
        self.setFixedSize(700, 620)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; }}
        """)
        self._build()
        self._render_image()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        # ---- Title
        addr = QLabel(self.property_data.get("address", "Property"))
        addr.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        addr.setWordWrap(True)
        layout.addWidget(addr)

        # ---- Image area
        img_frame = QFrame()
        img_frame.setFixedHeight(IMAGE_H)
        img_frame.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
        """)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(8, 8, 8, 8)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            f"background: {theme.BG_SUBTLE}; "
            f"border-radius: {theme.RADIUS_MD}px; "
            f"font-size: 64px; color: {theme.TEXT_FAINT};"
        )
        img_layout.addWidget(self.image_label)
        layout.addWidget(img_frame)

        # ---- Image navigation
        nav = QHBoxLayout()
        nav.addStretch()

        self.btn_prev = QPushButton("← Previous")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setFixedHeight(34)
        self.btn_prev.setStyleSheet(theme.button_qss("secondary"))
        self.btn_prev.clicked.connect(self._on_prev)
        nav.addWidget(self.btn_prev)

        self.counter = QLabel("0 / 0")
        self.counter.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_BASE}px; "
            f"padding: 0 12px;"
        )
        nav.addWidget(self.counter)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedHeight(34)
        self.btn_next.setStyleSheet(theme.button_qss("secondary"))
        self.btn_next.clicked.connect(self._on_next)
        nav.addWidget(self.btn_next)

        nav.addStretch()
        layout.addLayout(nav)

        # ---- Details
        details_frame = QFrame()
        details_frame.setStyleSheet(theme.card_qss())
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(18, 14, 18, 14)
        details_layout.setSpacing(8)

        def kv(label, value):
            row = QHBoxLayout()
            l1 = QLabel(label)
            l1.setFixedWidth(120)
            l1.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-weight: bold; "
                f"font-size: {theme.FS_SM}px;"
            )
            l2 = QLabel(str(value or "—"))
            l2.setWordWrap(True)
            l2.setStyleSheet(
                f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px;"
            )
            row.addWidget(l1)
            row.addWidget(l2, stretch=1)
            details_layout.addLayout(row)

        d = self.property_data
        price = d.get("listing_price")
        price_str = f"R{price:,.2f} / month" if price else "—"
        kv("Rent:", price_str)
        kv("Type:", d.get("property_type", ""))
        kv("Status:", d.get("status", ""))
        kv("Details:", d.get("build_details", ""))

        layout.addWidget(details_frame)

        # ---- Close
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet(theme.button_qss("secondary"))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    # ------------------------------------------------------------------ gallery
    def _render_image(self):
        total = len(self.images)
        if total == 0:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("🏠")
            self.counter.setText("0 / 0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        img = self.images[self.current_index]
        path = img.get("full_path")
        if path and os.path.isfile(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    IMAGE_W, IMAGE_H - 16, Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled)
                self.image_label.setText("")
            else:
                self.image_label.setText("🖼")
        else:
            self.image_label.setText("🖼")

        self.counter.setText(f"{self.current_index + 1} / {total}")
        self.btn_prev.setEnabled(total > 1)
        self.btn_next.setEnabled(total > 1)

    def _on_prev(self):
        if not self.images:
            return
        self.current_index = (self.current_index - 1) % len(self.images)
        self._render_image()

    def _on_next(self):
        if not self.images:
            return
        self.current_index = (self.current_index + 1) % len(self.images)
        self._render_image()