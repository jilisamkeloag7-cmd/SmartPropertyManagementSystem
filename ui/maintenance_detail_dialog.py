print(">>> maintenance_detail_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox
)
from Services.maintenance_service import ALLOWED_TRANSITIONS


class MaintenanceDetailDialog(QDialog):
    """Shows request details and lets a manager change status."""

    def __init__(self, parent=None, request_data: dict | None = None,
                 session_user=None):
        super().__init__(parent)
        self.request_data = request_data or {}
        self.session_user = session_user or {}
        self.setWindowTitle(f"Request #{self.request_data.get('request_id', '')}")
        self.setFixedSize(520, 480)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QComboBox {
                padding: 8px 10px; border: 2px solid #ecf0f1;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QComboBox:focus { border-color: #3498db; }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        d = self.request_data
        title = QLabel(f"Request #{d.get('request_id', '')}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        def kv(label, value):
            row = QHBoxLayout()
            l1 = QLabel(label)
            l1.setFixedWidth(120)
            l1.setStyleSheet("color: #7f8c8d; font-weight: bold; font-size: 12px;")
            l2 = QLabel(str(value or "—"))
            l2.setWordWrap(True)
            l2.setStyleSheet("color: #2c3e50; font-size: 13px;")
            row.addWidget(l1)
            row.addWidget(l2, stretch=1)
            layout.addLayout(row)

        kv("Property:", d.get("property_address", ""))
        kv("Submitted by:", d.get("submitter_name", ""))
        kv("Priority:", d.get("priority", ""))
        kv("Status:", d.get("status", ""))
        kv("Created:", d.get("created_at", ""))
        kv("Completed:", d.get("completed_at", "") or "—")
        kv("Description:", d.get("description", ""))

        layout.addSpacing(10)

        # ---- Status change section (managers only)
        role = self.session_user.get("role", "")
        self.is_manager = role in ("Administrator", "Property Manager")

        if self.is_manager:
            current = d.get("status", "")
            allowed = sorted(ALLOWED_TRANSITIONS.get(current, set()))
            if allowed:
                lbl = QLabel("Change status to:")
                lbl.setStyleSheet(
                    "color: #2c3e50; font-weight: bold; font-size: 13px;"
                )
                layout.addWidget(lbl)

                self.status_combo = QComboBox()
                self.status_combo.addItems(allowed)
                layout.addWidget(self.status_combo)

                btn = QPushButton("Update Status")
                btn.setFixedHeight(40)
                btn.setStyleSheet(
                    "background: #3498db; color: white; border: none; "
                    "border-radius: 8px; font-weight: bold; font-size: 13px;"
                )
                btn.clicked.connect(self._on_update)
                layout.addWidget(btn)
            else:
                lbl = QLabel("This request is closed — no further transitions.")
                lbl.setStyleSheet("color: #95a5a6; font-style: italic;")
                layout.addWidget(lbl)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet(
            "background: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 8px; font-weight: bold; font-size: 13px;"
        )
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def _on_update(self):
        self.new_status = self.status_combo.currentText()
        self.accept()