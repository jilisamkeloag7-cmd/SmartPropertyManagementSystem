print(">>> notification_popup.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget, QMessageBox
)
from PySide6.QtCore import Qt


PRIORITY_COLORS = {
    "Low":      "#95a5a6",
    "Normal":   "#3498db",
    "High":     "#e67e22",
    "Urgent":   "#c0392b",
}


class NotificationPopup(QDialog):
    """Notification centre, opened by the dashboard bell."""

    def __init__(self, parent=None, controller=None, user_id: int | None = None,
                 on_close_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.on_close_callback = on_close_callback
        self.setWindowTitle("Notifications")
        self.setFixedSize(520, 560)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; }
        """)
        self._build()
        self._load()

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # ---- Header
        header = QHBoxLayout()
        title = QLabel("🔔 Notifications")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()

        self.btn_mark_all = QPushButton("Mark all read")
        self.btn_mark_all.setStyleSheet(
            "background: transparent; color: #3498db; border: none; "
            "font-size: 12px; font-weight: bold; padding: 6px 8px;"
        )
        self.btn_mark_all.clicked.connect(self._on_mark_all)
        header.addWidget(self.btn_mark_all)

        self.btn_prefs = QPushButton("⚙ Preferences")
        self.btn_prefs.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; "
            "font-size: 12px; padding: 6px 8px;"
        )
        self.btn_prefs.clicked.connect(self._on_open_prefs)
        header.addWidget(self.btn_prefs)

        layout.addLayout(header)

        # ---- Scroll area holding notification cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self.container = QWidget()
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
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet(
            "background: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 8px; font-weight: bold; padding: 0 20px;"
        )
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    # ------------------------------------------------------------------ load
    def _load(self):
        # Clear existing cards (except the trailing stretch)
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
            empty.setStyleSheet("color: #95a5a6; font-size: 13px; padding: 30px;")
            self.container_layout.insertWidget(0, empty)
            return

        for idx, n in enumerate(rows):
            self.container_layout.insertWidget(idx, self._build_card(n))

    def _build_card(self, n: dict):
        card = QFrame()
        unread = n["is_unread"]
        priority = n.get("priority", "Normal")
        color = PRIORITY_COLORS.get(priority, "#3498db")

        if unread:
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-left: 4px solid {color};
                    border-top: 1px solid #ecf0f1;
                    border-right: 1px solid #ecf0f1;
                    border-bottom: 1px solid #ecf0f1;
                    border-radius: 8px;
                }}
                QFrame:hover {{ background: #f8fbfe; }}
            """)
        else:
            card.setStyleSheet("""
                QFrame {
                    background: #fafbfc;
                    border-left: 4px solid #d6dde3;
                    border-top: 1px solid #ecf0f1;
                    border-right: 1px solid #ecf0f1;
                    border-bottom: 1px solid #ecf0f1;
                    border-radius: 8px;
                }
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
            title.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        else:
            title.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        top.addWidget(title)
        top.addStretch()

        ts = QLabel(str(n.get("created_at", ""))[:16])
        ts.setStyleSheet("font-size: 11px; color: #95a5a6;")
        top.addWidget(ts)
        inner.addLayout(top)

        msg = QLabel(n.get("message") or "")
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        inner.addWidget(msg)

        return card

    # ------------------------------------------------------------------ handlers
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

    # ------------------------------------------------------------------ close
    def accept(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().accept()

    def reject(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().reject()