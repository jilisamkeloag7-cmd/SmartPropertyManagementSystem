print(">>> notification_popup.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget
)
from PySide6.QtCore import Qt
from ui import theme


PRIORITY_COLORS = {
    "Low":      theme.TEXT_FAINT,
    "Normal":   theme.PRIMARY,
    "High":     theme.WARNING_HOVER,
    "Urgent":   theme.DANGER_HOVER,
}


class NotificationPopup(QDialog):
    def __init__(self, parent=None, controller=None, user_id: int | None = None,
                 on_close_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.on_close_callback = on_close_callback
        self.setWindowTitle("Notifications")
        self.setFixedSize(540, 600)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; }}
        """)
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        # ---- Header
        header = QHBoxLayout()
        title = QLabel("🔔 Notifications")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
        header.addStretch()

        self.btn_mark_all = QPushButton("Mark all read")
        self.btn_mark_all.setCursor(Qt.PointingHandCursor)
        self.btn_mark_all.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.PRIMARY};
                border: none;
                font-size: {theme.FS_SM}px;
                font-weight: bold;
                padding: 6px 8px;
            }}
            QPushButton:hover {{ color: {theme.PRIMARY_HOVER}; }}
        """)
        self.btn_mark_all.clicked.connect(self._on_mark_all)
        header.addWidget(self.btn_mark_all)

        self.btn_prefs = QPushButton("⚙ Preferences")
        self.btn_prefs.setCursor(Qt.PointingHandCursor)
        self.btn_prefs.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                font-size: {theme.FS_SM}px;
                padding: 6px 8px;
            }}
            QPushButton:hover {{ color: {theme.PRIMARY}; }}
        """)
        self.btn_prefs.clicked.connect(self._on_open_prefs)
        header.addWidget(self.btn_prefs)

        layout.addLayout(header)

        # ---- Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {theme.BG_APP}; }}")

        self.container = QWidget()
        self.container.setStyleSheet(f"background: {theme.BG_APP};")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch()
        scroll.setWidget(self.container)
        layout.addWidget(scroll, stretch=1)

        # ---- Footer
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(38)
        btn_close.setStyleSheet(theme.button_qss("secondary"))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _load(self):
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.user_id:
            return

        rows = self.controller.list_for_user(self.user_id)

        if not rows:
            empty = QLabel("No notifications yet.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_BASE}px; "
                f"padding: 30px;"
            )
            self.container_layout.insertWidget(0, empty)
            return

        for idx, n in enumerate(rows):
            self.container_layout.insertWidget(idx, self._build_card(n))

    def _build_card(self, n: dict):
        card = QFrame()
        unread = n["is_unread"]
        priority = n.get("priority", "Normal")
        color = PRIORITY_COLORS.get(priority, theme.PRIMARY)

        if unread:
            card.setStyleSheet(f"""
                QFrame {{
                    background: {theme.BG_CARD};
                    border-left: 4px solid {color};
                    border-top: 1px solid {theme.BORDER};
                    border-right: 1px solid {theme.BORDER};
                    border-bottom: 1px solid {theme.BORDER};
                    border-radius: 8px;
                }}
                QFrame:hover {{ background: {theme.BG_SUBTLE}; }}
            """)
        else:
            card.setStyleSheet(f"""
                QFrame {{
                    background: {theme.BG_SUBTLE};
                    border-left: 4px solid {theme.TEXT_FAINT};
                    border-top: 1px solid {theme.BORDER};
                    border-right: 1px solid {theme.BORDER};
                    border-bottom: 1px solid {theme.BORDER};
                    border-radius: 8px;
                }}
            """)

        card.setCursor(Qt.PointingHandCursor)
        if unread:
            card.mousePressEvent = lambda e, nid=n["notification_id"]: self._on_card_click(nid)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(12, 10, 12, 10)
        inner.setSpacing(4)

        top = QHBoxLayout()
        title = QLabel(n.get("title") or "(no title)")
        if unread:
            title.setStyleSheet(
                f"font-size: {theme.FS_BASE}px; font-weight: bold; "
                f"color: {theme.TEXT_MAIN};"
            )
        else:
            title.setStyleSheet(
                f"font-size: {theme.FS_BASE}px; color: {theme.TEXT_MUTED};"
            )
        top.addWidget(title)
        top.addStretch()

        ts = QLabel(str(n.get("created_at", ""))[:16])
        ts.setStyleSheet(f"font-size: {theme.FS_XS}px; color: {theme.TEXT_FAINT};")
        top.addWidget(ts)
        inner.addLayout(top)

        msg = QLabel(n.get("message") or "")
        msg.setWordWrap(True)
        msg.setStyleSheet(
            f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MUTED};"
        )
        inner.addWidget(msg)

        return card

    def _on_card_click(self, notification_id: int):
        self.controller.mark_read(notification_id)
        self._load()
        if self.on_close_callback:
            self.on_close_callback()

    def _on_mark_all(self):
        if not self.user_id:
            return
        ok, msg = self.controller.mark_all_read(self.user_id)
        if ok:
            self._load()
            if self.on_close_callback:
                self.on_close_callback()

    def _on_open_prefs(self):
        from ui.notification_preferences_dialog import NotificationPreferencesDialog
        dlg = NotificationPreferencesDialog(
            self, controller=self.controller, user_id=self.user_id
        )
        dlg.exec()

    def accept(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().accept()

    def reject(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().reject()