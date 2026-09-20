print(">>> property_card.py V1 <<<")

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui import theme


CARD_W = 260
CARD_H = 230
IMAGE_H = 120


class PropertyCard(QFrame):
    """
    Card widget displaying a property.
    - Image area (placeholder for now; image support in Phase 5)
    - Address
    - Type • Status line
    - Optional footer detail (build details snippet)
    - Optional click handler + optional action button
    """

    def __init__(self, property_data: dict, parent=None,
                 on_click=None, action_label=None, on_action=None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.on_click = on_click
        self.action_label = action_label
        self.on_action = on_action
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

        # ---- Image area (placeholder)
        image_area = QLabel("🏠")
        image_area.setAlignment(Qt.AlignCenter)
        image_area.setFixedHeight(IMAGE_H)
        image_area.setStyleSheet(f"""
            background: {theme.PRIMARY_SOFT};
            border-top-left-radius: {theme.RADIUS_LG}px;
            border-top-right-radius: {theme.RADIUS_LG}px;
            font-size: 48px;
            color: {theme.PRIMARY};
        """)
        outer.addWidget(image_area)

        # ---- Info area
        info = QVBoxLayout()
        info.setContentsMargins(14, 12, 14, 12)
        info.setSpacing(4)

        addr = QLabel(self.property_data.get("address", "(no address)"))
        addr.setWordWrap(True)
        addr.setMaximumHeight(40)
        addr.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN}; border: none; background: transparent;"
        )
        info.addWidget(addr)

        # Type • Status
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

        # Build details snippet
        details = self.property_data.get("build_details") or ""
        if details:
            snippet = QLabel(details[:60] + ("…" if len(details) > 60 else ""))
            snippet.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px; "
                f"border: none; background: transparent;"
            )
            snippet.setWordWrap(True)
            info.addWidget(snippet)

        info.addStretch()

        # Optional action button
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