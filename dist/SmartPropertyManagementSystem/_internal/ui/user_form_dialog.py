print(">>> user_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)

ROLES = ["Administrator", "Property Manager", "Owner", "Tenant"]
STATUSES = ["Active", "Inactive"]


class UserFormDialog(QDialog):
    """Modal for adding or editing a user."""

    def __init__(self, parent=None, user_data: dict | None = None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.is_edit = bool(user_data and user_data.get("user_id"))
        self.setWindowTitle("Edit User" if self.is_edit else "Add User")
        self.setFixedSize(480, 500)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QLineEdit, QComboBox {
                padding: 8px 10px; border: 2px solid #ecf0f1;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #3498db; }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Edit User" if self.is_edit else "Add User")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name = QLineEdit(self.user_data.get("name", ""))
        self.name.setPlaceholderText("Full name")
        form.addRow("Name *", self.name)

        self.id_number = QLineEdit(self.user_data.get("id_number", ""))
        self.id_number.setPlaceholderText("e.g. 9001015009087")
        self.id_number.setReadOnly(self.is_edit)   # ID number is not editable
        if self.is_edit:
            self.id_number.setStyleSheet("background: #f0f4f8; color: #7f8c8d;")
        form.addRow("ID Number *", self.id_number)

        self.email = QLineEdit(self.user_data.get("email", ""))
        self.email.setPlaceholderText("user@example.com")
        form.addRow("Email *", self.email)

        self.phone = QLineEdit(self.user_data.get("phone", "") or "")
        self.phone.setPlaceholderText("Optional")
        form.addRow("Phone", self.phone)

        self.role = QComboBox()
        self.role.addItems(ROLES)
        if self.user_data.get("role"):
            self.role.setCurrentText(self.user_data["role"])
        form.addRow("Role *", self.role)

        self.status = QComboBox()
        self.status.addItems(STATUSES)
        if self.user_data.get("status"):
            self.status.setCurrentText(self.user_data["status"])
        form.addRow("Status *", self.status)

        # Password — only required on create, optional on edit (blank = keep)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        if self.is_edit:
            self.password.setPlaceholderText("Leave blank to keep current password")
        else:
            self.password.setPlaceholderText("Minimum 6 characters")
        form.addRow("Password *" if not self.is_edit else "New Password", self.password)

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
        if not self.name.text().strip():
            QMessageBox.warning(self, "Missing field", "Name is required.")
            return
        if not self.is_edit and not self.id_number.text().strip():
            QMessageBox.warning(self, "Missing field", "ID Number is required.")
            return
        if "@" not in self.email.text():
            QMessageBox.warning(self, "Invalid email", "Enter a valid email address.")
            return
        if not self.is_edit and len(self.password.text()) < 6:
            QMessageBox.warning(self, "Weak password",
                                "Password must be at least 6 characters.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "id_number": self.id_number.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "role": self.role.currentText(),
            "status": self.status.currentText(),
            "password": self.password.text(),
        }