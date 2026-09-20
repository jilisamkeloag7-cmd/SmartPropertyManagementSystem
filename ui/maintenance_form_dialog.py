print(">>> maintenance_form_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit,
    QComboBox, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Services.maintenance_service import VALID_PRIORITIES
from ui import theme


class MaintenanceFormDialog(QDialog):
    def __init__(self, parent=None, session_user=None):
        super().__init__(parent)
        self.session_user = session_user or {}
        self.setWindowTitle("New Maintenance Request")
        self.setFixedSize(520, 460)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("New Maintenance Request")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel("Describe the issue and its urgency")
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.property_combo = QComboBox()
        self.property_combo.setFixedHeight(40)
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
        self.property_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Property"), self.property_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(sorted(VALID_PRIORITIES))
        self.priority_combo.setCurrentText("Medium")
        self.priority_combo.setFixedHeight(40)
        self.priority_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Priority"), self.priority_combo)

        self.description = QTextEdit()
        self.description.setFixedHeight(140)
        self.description.setPlaceholderText(
            "Describe the issue (e.g. leaking kitchen tap, broken window)"
        )
        self.description.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Description"), self.description)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        save_btn = buttons.button(QDialogButtonBox.Save)
        save_btn.setText("Submit")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(theme.button_qss("primary"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; "
            f"font-size: {theme.FS_SM}px; font-weight: bold;"
        )
        return lbl

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