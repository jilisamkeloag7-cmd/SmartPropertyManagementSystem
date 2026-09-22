print(">>> property_card.py V3 <<<")

import os
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ui import theme
from Controllers.property_controller import PropertyController


CARD_W = 260
CARD_H = 260
IMAGE_H = 130


class PropertyCard(QFrame):
    def __init__(self, property_data: dict, parent=None,
                 on_click=None, action_label=None, on_action=None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.on_click = on_click
        self.action_label = action_label
        self.on_action = on_action
        self._controller = PropertyController()
        self._build()

    def _build(self):
        self.setFixedSize(CARD_W, CARD_H)
        self.setStyleSheet(f"""
            PropertyCard {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
            PropertyCard:hover {{
                border-color: {theme.PRIMARY};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---- Image area
        image_area = QLabel()
        image_area.setAlignment(Qt.AlignCenter)
        image_area.setFixedHeight(IMAGE_H)
        image_area.setStyleSheet(f"""
            background: {theme.PRIMARY_SOFT};
            border-top-left-radius: {theme.RADIUS_LG}px;
            border-top-right-radius: {theme.RADIUS_LG}px;
            font-size: 48px;
            color: {theme.PRIMARY};
        """)

        # Try to load first image
        img_path = None
        try:
            img_path = self._controller.first_image_path(
                self.property_data.get("property_id")
            )
        except Exception:
            pass

        if img_path and os.path.isfile(img_path):
            pix = QPixmap(img_path)
            if not pix.isNull():
                scaled = pix.scaled(
                    CARD_W, IMAGE_H, Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
                # Crop to exact size (centred)
                x = max(0, (scaled.width() - CARD_W) // 2)
                y = max(0, (scaled.height() - IMAGE_H) // 2)
                cropped = scaled.copy(x, y, CARD_W, IMAGE_H)
                image_area.setPixmap(cropped)
            else:
                image_area.setText("🏠")
        else:
            image_area.setText("🏠")

        outer.addWidget(image_area)

        # ---- Info area
        info = QVBoxLayout()
        info.setContentsMargins(14, 12, 14, 12)
        info.setSpacing(6)

        addr = QLabel(self.property_data.get("address", "(no address)"))
        addr.setWordWrap(True)
        addr.setMaximumHeight(36)
        addr.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN}; border: none; background: transparent;"
        )
        info.addWidget(addr)

        # ---- Price
        price = self.property_data.get("listing_price")
        if price is not None and price > 0:
            price_row = QHBoxLayout()
            price_row.setSpacing(4)

            amount = QLabel(f"R{price:,.0f}")
            amount.setStyleSheet(
                f"font-size: {theme.FS_XL}px; font-weight: bold; "
                f"color: {theme.PRIMARY}; border: none; background: transparent;"
            )
            price_row.addWidget(amount)

            per_month = QLabel("/ month")
            per_month.setStyleSheet(
                f"font-size: {theme.FS_XS}px; color: {theme.TEXT_MUTED}; "
                f"border: none; background: transparent;"
            )
            per_month.setAlignment(Qt.AlignBottom)
            price_row.addWidget(per_month)
            price_row.addStretch()
            info.addLayout(price_row)
        else:
            no_price = QLabel("Price on request")
            no_price.setStyleSheet(
                f"font-size: {theme.FS_BASE}px; font-style: italic; "
                f"color: {theme.TEXT_FAINT}; border: none; background: transparent;"
            )
            info.addWidget(no_price)

        # ---- Badges
        meta = QHBoxLayout()
        meta.setSpacing(6)

        ptype = QLabel(self.property_data.get("property_type") or "—")
        ptype.setStyleSheet(f"""
            background: {theme.BG_SUBTLE};
            color: {theme.TEXT_MUTED};
            padding: 2px 8px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        meta.addWidget(ptype)

        status = self.property_data.get("status") or "—"
        status_colors = {
            "Available":         (theme.SUCCESS_SOFT, theme.SUCCESS_HOVER),
            "Occupied":          (theme.INFO_SOFT, theme.INFO),
            "Under Maintenance": (theme.WARNING_SOFT, theme.WARNING_HOVER),
            "Archived":          (theme.BG_SUBTLE, theme.TEXT_FAINT),
        }
        bg, fg = status_colors.get(status, (theme.BG_SUBTLE, theme.TEXT_MUTED))
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(f"""
            background: {bg};
            color: {fg};
            padding: 2px 8px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        meta.addWidget(status_lbl)
        meta.addStretch()
        info.addLayout(meta)

        info.addStretch()

        if self.action_label and self.on_action:
            btn = QPushButton(self.action_label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setStyleSheet(theme.button_qss("primary"))
            btn.clicked.connect(self._handle_action)
            info.addWidget(btn)

        outer.addLayout(info)

    def _handle_action(self):
        if self.on_action:
            self.on_action(self.property_data)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click(self.property_data)
        super().mousePressEvent(event)