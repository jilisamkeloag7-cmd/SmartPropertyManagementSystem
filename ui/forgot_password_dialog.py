print(">>> forgot_password_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from Controllers.auth_controller import AuthController
from ui import theme


class ForgotPasswordDialog(QDialog):
    """3-step password recovery: email → security question → new password."""

    def __init__(self, parent=None, prefill_email: str = ""):
        super().__init__(parent)
        self.auth = AuthController()
        self.step = 1
        self.user_email = ""
        self.user_answer = ""
        self.setWindowTitle("Reset Password")
        self.setFixedSize(500, 460)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()
        if prefill_email:
            self.email_input.setText(prefill_email)

    def _build(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(28, 26, 28, 26)
        self.layout.setSpacing(14)

        self.title_label = QLabel("Reset Password")
        self.title_label.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        self.layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        self.layout.addWidget(self.subtitle_label)

        # ---- Dynamic content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self.layout.addLayout(self.content_layout)

        self.layout.addStretch()

        # ---- Nav buttons
        nav = QHBoxLayout()
        nav.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setFixedHeight(42)
        self.btn_cancel.setStyleSheet(theme.button_qss("secondary"))
        self.btn_cancel.clicked.connect(self.reject)
        nav.addWidget(self.btn_cancel)

        self.btn_next = QPushButton("Continue")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedHeight(42)
        self.btn_next.setStyleSheet(theme.button_qss("primary"))
        self.btn_next.clicked.connect(self._on_next)
        nav.addWidget(self.btn_next)

        self.layout.addLayout(nav)

        # Render step 1
        self._render_step_1()

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px; "
            f"font-weight: bold;"
        )
        return lbl

    # ------------------------------------------------------------------ Step 1
    def _render_step_1(self):
        self._clear_content()
        self.title_label.setText("Reset Password")
        self.subtitle_label.setText(
            "Enter the email address associated with your account. We'll "
            "show your security question."
        )
        self.btn_next.setText("Continue")

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        self.email_input.setFixedHeight(42)
        self.email_input.setStyleSheet(theme.input_qss())
        self.email_input.returnPressed.connect(self._on_next)
        form.addRow(self._label("Email *"), self.email_input)

        wrapper = QVBoxLayout()
        wrapper.addLayout(form)
        self.content_layout.addLayout(wrapper)

    def _submit_step_1(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Missing email", "Please enter your email.")
            return

        question = self.auth.get_security_question(email)
        if not question:
            QMessageBox.warning(
                self, "No recovery setup",
                "No account found with that email, or no security question "
                "is configured for it. Please contact an administrator."
            )
            return

        self.user_email = email
        self.step = 2
        self._render_step_2(question)

    # ------------------------------------------------------------------ Step 2
    def _render_step_2(self, question: str):
        self._clear_content()
        self.title_label.setText("Security Question")
        self.subtitle_label.setText(
            "Answer your security question. Answers are case-insensitive."
        )
        self.btn_next.setText("Verify")

        q_lbl = QLabel(question)
        q_lbl.setWordWrap(True)
        q_lbl.setStyleSheet(f"""
            background: {theme.BG_CARD};
            border: 1px solid {theme.BORDER};
            border-radius: {theme.RADIUS_MD}px;
            padding: 14px;
            color: {theme.TEXT_MAIN};
            font-size: {theme.FS_BASE}px;
        """)
        self.content_layout.addWidget(q_lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Your answer")
        self.answer_input.setFixedHeight(42)
        self.answer_input.setStyleSheet(theme.input_qss())
        self.answer_input.returnPressed.connect(self._on_next)
        form.addRow(self._label("Answer *"), self.answer_input)

        self.content_layout.addLayout(form)

    def _submit_step_2(self):
        answer = self.answer_input.text()
        ok, msg = self.auth.verify_security_answer(self.user_email, answer)
        if not ok:
            QMessageBox.warning(self, "Incorrect", msg)
            return
        self.user_answer = answer
        self.step = 3
        self._render_step_3()

    # ------------------------------------------------------------------ Step 3
    def _render_step_3(self):
        self._clear_content()
        self.title_label.setText("Set New Password")
        self.subtitle_label.setText(
            "Choose a new password. Minimum 6 characters."
        )
        self.btn_next.setText("Reset Password")

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("New password")
        self.new_password.setFixedHeight(42)
        self.new_password.setStyleSheet(theme.input_qss())
        form.addRow(self._label("New Password *"), self.new_password)

        self.new_password2 = QLineEdit()
        self.new_password2.setEchoMode(QLineEdit.Password)
        self.new_password2.setPlaceholderText("Confirm new password")
        self.new_password2.setFixedHeight(42)
        self.new_password2.setStyleSheet(theme.input_qss())
        self.new_password2.returnPressed.connect(self._on_next)
        form.addRow(self._label("Confirm *"), self.new_password2)

        self.content_layout.addLayout(form)

    def _submit_step_3(self):
        p1 = self.new_password.text()
        p2 = self.new_password2.text()
        if p1 != p2:
            QMessageBox.warning(self, "Passwords don't match",
                                "Please make sure both fields match.")
            return
        if len(p1) < 6:
            QMessageBox.warning(self, "Password too short",
                                "Minimum 6 characters.")
            return

        ok, msg = self.auth.reset_password(self.user_email, self.user_answer, p1)
        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        QMessageBox.information(self, "Success", msg)
        self.accept()

    # ------------------------------------------------------------------ nav
    def _on_next(self):
        if self.step == 1:
            self._submit_step_1()
        elif self.step == 2:
            self._submit_step_2()
        else:
            self._submit_step_3()

