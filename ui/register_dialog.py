
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from Controllers.auth_controller import AuthController
from ui import theme


SECURITY_QUESTIONS = [
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first pet?",
    "What was the model of your first car?",
    "What was the name of your first school?",
]


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = AuthController()
        self.setWindowTitle("Create Account")
        self.setFixedSize(560, 740)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Create Account")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Register as a Tenant to apply for leases, an Owner to list "
            "properties, or a Property Manager to manage listings."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Tenant", "Owner", "Property Manager"])
        self.role_combo.setFixedHeight(40)
        self.role_combo.setStyleSheet(theme.input_qss())
        self.role_combo.currentTextChanged.connect(self._on_role_changed)
        form.addRow(self._label("I want to register as"), self.role_combo)

        # Role note (dynamic per selection)
        self.role_note = QLabel("")
        self.role_note.setWordWrap(True)
        self.role_note.setStyleSheet(f"""
            color: {theme.INFO};
            background: {theme.INFO_SOFT};
            padding: 8px 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
        """)
        form.addRow("", self.role_note)
        self._on_role_changed("Tenant")

        self.name = QLineEdit()
        self.name.setPlaceholderText("Full name")
        self.name.setFixedHeight(40)
        self.name.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Full Name *"), self.name)

        self.id_number = QLineEdit()
        self.id_number.setPlaceholderText("e.g. 9001015009087")
        self.id_number.setFixedHeight(40)
        self.id_number.setStyleSheet(theme.input_qss())
        form.addRow(self._label("ID / Passport Number *"), self.id_number)

        self.email = QLineEdit()
        self.email.setPlaceholderText("you@example.com")
        self.email.setFixedHeight(40)
        self.email.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Email *"), self.email)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Optional")
        self.phone.setFixedHeight(40)
        self.phone.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Phone"), self.phone)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Minimum 6 characters")
        self.password.setFixedHeight(40)
        self.password.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Password *"), self.password)

        self.password2 = QLineEdit()
        self.password2.setEchoMode(QLineEdit.Password)
        self.password2.setPlaceholderText("Confirm password")
        self.password2.setFixedHeight(40)
        self.password2.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Confirm Password *"), self.password2)

        layout.addLayout(form)

        sec_lbl = QLabel("Account Recovery")
        sec_lbl.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN}; padding-top: 6px;"
        )
        layout.addWidget(sec_lbl)

        sec_hint = QLabel(
            "Choose a question only you can answer. You'll use it to reset "
            "your password if you forget it."
        )
        sec_hint.setWordWrap(True)
        sec_hint.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px;"
        )
        layout.addWidget(sec_hint)

        sec_form = QFormLayout()
        sec_form.setSpacing(10)
        sec_form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.question_combo = QComboBox()
        self.question_combo.addItems(SECURITY_QUESTIONS)
        self.question_combo.setFixedHeight(40)
        self.question_combo.setStyleSheet(theme.input_qss())
        sec_form.addRow(self._label("Question *"), self.question_combo)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Your answer (case-insensitive)")
        self.answer.setFixedHeight(40)
        self.answer.setStyleSheet(theme.input_qss())
        sec_form.addRow(self._label("Answer *"), self.answer)

        layout.addLayout(sec_form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Create Account")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(42)
        ok_btn.setStyleSheet(theme.button_qss("primary"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
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

    def _on_role_changed(self, role):
        notes = {
            "Tenant": (
                "You can browse properties, apply for leases, and submit "
                "maintenance requests once you have a lease."
            ),
            "Owner": (
                "You can submit properties for approval and see reports on "
                "your portfolio once they're live."
            ),
            "Property Manager": (
                "⚠  Manager accounts require administrator approval. "
                "You will not be able to log in until your account is approved."
            ),
        }
        self.role_note.setText(notes.get(role, ""))

    def _on_accept(self):
        if self.password.text() != self.password2.text():
            QMessageBox.warning(self, "Passwords don't match",
                                "Please make sure both password fields match.")
            return
        if len(self.password.text()) < 6:
            QMessageBox.warning(self, "Password too short",
                                "Password must be at least 6 characters.")
            return
        if len(self.answer.text().strip()) < 3:
            QMessageBox.warning(self, "Answer too short",
                                "Security answer must be at least 3 characters.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "role_str": self.role_combo.currentText(),
            "name": self.name.text().strip(),
            "id_number": self.id_number.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "password": self.password.text(),
            "security_question": self.question_combo.currentText(),
            "security_answer": self.answer.text().strip(),
        }
