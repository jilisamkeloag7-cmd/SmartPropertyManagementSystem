print(">>> maintenance_detail_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox
)
from PySide6.QtCore import Qt
from Services.maintenance_service import ALLOWED_TRANSITIONS
from ui import theme


class MaintenanceDetailDialog(QDialog):
    def __init__(self, parent=None, request_data: dict | None = None,
                 session_user=None):
        super().__init__(parent)
        self.request_data = request_data or {}
        self.session_user = session_user or {}
        self.setWindowTitle(f"Request #{self.request_data.get('request_id', '')}")
        self.setFixedSize(540, 560)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self.new_status = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        d = self.request_data
        title = QLabel(f"Request #{d.get('request_id', '')}")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        layout.addSpacing(4)

        def kv(label, value):
            row = QHBoxLayout()
            l1 = QLabel(label)
            l1.setFixedWidth(120)
            l1.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; "
                f"font-weight: bold; font-size: {theme.FS_SM}px;"
            )
            l2 = QLabel(str(value or "—"))
            l2.setWordWrap(True)
            l2.setStyleSheet(
                f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px;"
            )
            row.addWidget(l1)
            row.addWidget(l2, stretch=1)
            layout.addLayout(row)

        kv("Property:", d.get("property_address", ""))
        kv("Submitted by:", d.get("submitter_name", ""))
        kv("Priority:", d.get("priority", ""))
        kv("Status:", d.get("status", ""))
        kv("Created:", str(d.get("created_at", ""))[:16] if d.get("created_at") else "—")
        kv("Completed:", str(d.get("completed_at", ""))[:16] if d.get("completed_at") else "—")
        kv("Description:", d.get("description", ""))

        layout.addSpacing(10)

        role = self.session_user.get("role", "")
        self.is_manager = role in ("Administrator", "Property Manager")

        if self.is_manager:
            current = d.get("status", "")
            allowed = sorted(ALLOWED_TRANSITIONS.get(current, set()))
            if allowed:
                lbl = QLabel("Change status to:")
                lbl.setStyleSheet(
                    f"color: {theme.TEXT_MAIN}; font-weight: bold; "
                    f"font-size: {theme.FS_BASE}px;"
                )
                layout.addWidget(lbl)

                self.status_combo = QComboBox()
                self.status_combo.addItems(allowed)
                self.status_combo.setFixedHeight(40)
                self.status_combo.setStyleSheet(theme.input_qss())
                layout.addWidget(self.status_combo)

                btn = QPushButton("Update Status")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFixedHeight(42)
                btn.setStyleSheet(theme.button_qss("primary"))
                btn.clicked.connect(self._on_update)
                layout.addWidget(btn)
            else:
                lbl = QLabel("This request is closed — no further transitions.")
                lbl.setStyleSheet(
                    f"color: {theme.TEXT_FAINT}; font-style: italic;"
                )
                layout.addWidget(lbl)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedHeight(42)
        close_btn.setStyleSheet(theme.button_qss("secondary"))
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def _on_update(self):
        self.new_status = self.status_combo.currentText()
        self.accept()