print(">>> property_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox, QLabel, QMessageBox
)

PROPERTY_TYPES = ["House", "Apartment", "Commercial", "Other"]
STATUSES = ["Available", "Occupied", "Under Maintenance", "Archived"]


class PropertyFormDialog(QDialog):
    """Modal for adding or editing a property."""

    def __init__(self, parent=None, property_data: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.is_edit = bool(property_data and property_data.get("property_id"))
        self.setWindowTitle("Edit Property" if self.is_edit else "Add Property")
        self.setFixedSize(460, 420)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px 10px; border: 2px solid #ecf0f1;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                padding: 8px 18px; border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold; min-width: 90px;
            }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Edit Property" if self.is_edit else "Add Property")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.address = QLineEdit()
        self.address.setPlaceholderText("e.g. 12 Main Rd, Durban")
        self.address.setText(self.property_data.get("address", ""))
        form.addRow("Address *", self.address)

        self.ptype = QComboBox()
        self.ptype.addItems(PROPERTY_TYPES)
        if self.property_data.get("property_type"):
            self.ptype.setCurrentText(self.property_data["property_type"])
        form.addRow("Property Type *", self.ptype)

        self.status = QComboBox()
        self.status.addItems(STATUSES)
        if self.property_data.get("status"):
            self.status.setCurrentText(self.property_data["status"])
        form.addRow("Status *", self.status)

        self.build_details = QTextEdit()
        self.build_details.setPlaceholderText("e.g. 3 bed, 2 bath, built 2010")
        self.build_details.setFixedHeight(90)
        self.build_details.setText(self.property_data.get("build_details", "") or "")
        form.addRow("Build Details", self.build_details)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        save_btn = buttons.button(QDialogButtonBox.Save)
        save_btn.setStyleSheet(
            "background-color: #3498db; color: white; "
            "border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setStyleSheet(
            "background-color: #ecf0f1; color: #2c3e50; "
            "border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.address.text().strip():
            QMessageBox.warning(self, "Missing field", "Address is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "address": self.address.text().strip(),
            "property_type": self.ptype.currentText(),
            "status": self.status.currentText(),
            "build_details": self.build_details.toPlainText().strip(),
        }