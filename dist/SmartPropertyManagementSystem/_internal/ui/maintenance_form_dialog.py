print(">>> maintenance_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit,
    QComboBox, QDialogButtonBox, QLabel, QMessageBox
)
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Services.maintenance_service import VALID_PRIORITIES


class MaintenanceFormDialog(QDialog):
    """Submit a new maintenance request."""

    def __init__(self, parent=None, session_user=None):
        super().__init__(parent)
        self.session_user = session_user or {}
        self.setWindowTitle("New Maintenance Request")
        self.setFixedSize(500, 420)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QComboBox, QTextEdit {
                padding: 8px 10px; border: 2px solid #ecf0f1;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QComboBox:focus, QTextEdit:focus { border-color: #3498db; }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("New Maintenance Request")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # Property dropdown — for Tenant: only their leased properties.
        self.property_combo = QComboBox()
        role = self.session_user.get("role", "")
        uid = self.session_user.get("user_id")
        prop_repo = PropertyRepository()

        if role == "Tenant" and uid:
            lease_repo = LeaseRepository()
            my_leases = lease_repo.list_for_tenant(uid)
            allowed_pids = {l.property_id for l in my_leases if l.status == "Active"}
            for p in prop_repo.list_all():
                if p.property_id in allowed_pids:
                    self.property_combo.addItem(
                        f"#{p.property_id} — {p.address}", p.property_id
                    )
        else:
            for p in prop_repo.list_all():
                if p.status != "Archived":
                    self.property_combo.addItem(
                        f"#{p.property_id} — {p.address}", p.property_id
                    )
        form.addRow("Property *", self.property_combo)

        # Priority dropdown
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(sorted(VALID_PRIORITIES))
        self.priority_combo.setCurrentText("Medium")
        form.addRow("Priority *", self.priority_combo)

        # Description
        self.description = QTextEdit()
        self.description.setFixedHeight(140)
        self.description.setPlaceholderText(
            "Describe the issue (e.g. leaking kitchen tap, broken window)"
        )
        form.addRow("Description *", self.description)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setStyleSheet(
            "background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(
            "background-color: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if self.property_combo.count() == 0:
            QMessageBox.warning(
                self, "No property",
                "No eligible property available for a maintenance request."
            )
            return
        if not self.description.toPlainText().strip():
            QMessageBox.warning(self, "Missing field", "Description is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "property_id": self.property_combo.currentData(),
            "priority": self.priority_combo.currentText(),
            "description": self.description.toPlainText().strip(),
        }