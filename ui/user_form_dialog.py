print(">>> user_form_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from ui import theme


ROLES = ["Administrator", "Property Manager", "Owner", "Tenant"]
STATUSES = ["Active", "Inactive"]


class UserFormDialog(QDialog):
    def __init__(self, parent=None, user_data: dict | None = None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.is_edit = bool(user_data and user_data.get("user_id"))
        self.setWindowTitle("Edit User" if self.is_edit else "Add User")
        self.setFixedSize(500, 560)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("Edit User" if self.is_edit else "Add User")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Leave password blank to keep current" if self.is_edit
            else "Fill in the new user's details"
        )
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.name = QLineEdit(self.user_data.get("name", ""))
        self.name.setPlaceholderText("Full name")
        self.name.setFixedHeight(40)
        self.name.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Name"), self.name)

        self.id_number = QLineEdit(self.user_data.get("id_number", ""))
        self.id_number.setPlaceholderText("e.g. 9001015009087")
        self.id_number.setFixedHeight(40)
        self.id_number.setReadOnly(self.is_edit)
        self.id_number.setStyleSheet(
            theme.input_qss() if not self.is_edit
            else f"""
                QLineEdit {{
                    padding: 0 14px;
                    border: 2px solid {theme.BORDER};
                    border-radius: {theme.RADIUS_MD}px;
                    font-size: {theme.FS_MD}px;
                    color: {theme.TEXT_MUTED};
                    background: {theme.BG_SUBTLE};
                }}
            """
        )
        form.addRow(self._label("ID Number"), self.id_number)

        self.email = QLineEdit(self.user_data.get("email", ""))
        self.email.setPlaceholderText("user@example.com")
        self.email.setFixedHeight(40)
        self.email.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Email"), self.email)

        self.phone = QLineEdit(self.user_data.get("phone", "") or "")
        self.phone.setPlaceholderText("Optional")
        self.phone.setFixedHeight(40)
        self.phone.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Phone"), self.phone)

        self.role = QComboBox()
        self.role.addItems(ROLES)
        if self.user_data.get("role"):
            self.role.setCurrentText(self.user_data["role"])
        self.role.setFixedHeight(40)
        self.role.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Role"), self.role)

        self.status = QComboBox()
        self.status.addItems(STATUSES)
        if self.user_data.get("status"):
            self.status.setCurrentText(self.user_data["status"])
        self.status.setFixedHeight(40)
        self.status.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Status"), self.status)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(40)
        self.password.setPlaceholderText(
            "Leave blank to keep current" if self.is_edit
            else "Minimum 6 characters"
        )
        self.password.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Password"), self.password)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        save_btn = buttons.button(QDialogButtonBox.Save)
        save_btn.setText("Save")
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