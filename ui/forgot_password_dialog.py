print(">>> forgot_password_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QLabel,
    QPushButton, QWidget
)
from PySide6.QtCore import Qt
from Controllers.auth_controller import AuthController
from ui import theme


def _clear_layout(layout):
    """Recursively remove all widgets and nested layouts."""
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
            continue
        child = item.layout()
        if child is not None:
            _clear_layout(child)


class ForgotPasswordDialog(QDialog):
    """3-step password recovery: email → security question → new password."""

    def __init__(self, parent=None, prefill_email: str = ""):
        super().__init__(parent)
        self.auth = AuthController()
        self.step = 1
        self.user_email = ""
        self.user_answer = ""
        self.setWindowTitle("Reset Password")
        self.setFixedSize(500, 480)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build(prefill_email)

    # ------------------------------------------------------------------ shell
    def _build(self, prefill_email: str):
        shell = QVBoxLayout(self)
        shell.setContentsMargins(28, 26, 28, 26)
        shell.setSpacing(14)

        self.title_label = QLabel("Reset Password")
        self.title_label.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        shell.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        shell.addWidget(self.subtitle_label)

        shell.addSpacing(6)

        # ---- Dynamic content container (replaced on each step)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        shell.addWidget(self.content_widget, stretch=1)

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

        shell.addLayout(nav)

        self._render_step_1(prefill_email)

    # ------------------------------------------------------------------ helpers
    def _reset_content(self):
        _clear_layout(self.content_layout)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px; "
            f"font-weight: bold;"
        )
        return lbl

    # ------------------------------------------------------------------ Step 1
    def _render_step_1(self, prefill_email: str = ""):
        self._reset_content()
        self.step = 1
        self.title_label.setText("Reset Password")
        self.subtitle_label.setText(
            "Enter the email address associated with your account. "
            "We'll then show your security question."
        )
        self.btn_next.setText("Continue")

        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(0, 0, 0, 0)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        self.email_input.setFixedHeight(42)
        self.email_input.setStyleSheet(theme.input_qss())
        self.email_input.returnPressed.connect(self._on_next)
        if prefill_email:
            self.email_input.setText(prefill_email)
        form.addRow(self._label("Email *"), self.email_input)

        self.content_layout.addLayout(form)
        self.content_layout.addStretch()

    def _submit_step_1(self):
        email = self.email_input.text().strip()
        if not email:
            self._show_error("Please enter your email.")
            return

        question = self.auth.get_security_question(email)
        if not question:
            self._show_error(
                "No account found with that email, or no security question "
                "is configured for it. Please contact an administrator."
            )
            return

        self.user_email = email
        self._render_step_2(question)

    # ------------------------------------------------------------------ Step 2
    def _render_step_2(self, question: str):
        self._reset_content()
        self.step = 2
        self.title_label.setText("Security Question")
        self.subtitle_label.setText(
            "Answer your security question. Answers are case-insensitive."
        )
        self.btn_next.setText("Verify")

        # Question card
        q_lbl = QLabel(question)
        q_lbl.setWordWrap(True)
        q_lbl.setMinimumHeight(60)
        q_lbl.setStyleSheet(f"""
            background: {theme.BG_CARD};
            border: 1px solid {theme.BORDER};
            border-radius: {theme.RADIUS_MD}px;
            padding: 16px;
            color: {theme.TEXT_MAIN};
            font-size: {theme.FS_MD}px;
            font-weight: bold;
        """)
        self.content_layout.addWidget(q_lbl)

        self.content_layout.addSpacing(4)

        # Answer field
        ans_lbl = self._label("Your Answer *")
        self.content_layout.addWidget(ans_lbl)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer")
        self.answer_input.setFixedHeight(42)
        self.answer_input.setStyleSheet(theme.input_qss())
        self.answer_input.returnPressed.connect(self._on_next)
        self.content_layout.addWidget(self.answer_input)

        self.content_layout.addStretch()

    def _submit_step_2(self):
        answer = self.answer_input.text()
        ok, msg = self.auth.verify_security_answer(self.user_email, answer)
        if not ok:
            self._show_error(msg)
            return
        self.user_answer = answer
        self._render_step_3()

    # ------------------------------------------------------------------ Step 3
    def _render_step_3(self):
        self._reset_content()
        self.step = 3
        self.title_label.setText("Set New Password")
        self.subtitle_label.setText(
            "Choose a new password. Minimum 6 characters."
        )
        self.btn_next.setText("Reset Password")

        pwd_lbl = self._label("New Password *")
        self.content_layout.addWidget(pwd_lbl)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("New password")
        self.new_password.setFixedHeight(42)
        self.new_password.setStyleSheet(theme.input_qss())
        self.content_layout.addWidget(self.new_password)

        self.content_layout.addSpacing(4)

        confirm_lbl = self._label("Confirm Password *")
        self.content_layout.addWidget(confirm_lbl)

        self.new_password2 = QLineEdit()
        self.new_password2.setEchoMode(QLineEdit.Password)
        self.new_password2.setPlaceholderText("Confirm new password")
        self.new_password2.setFixedHeight(42)
        self.new_password2.setStyleSheet(theme.input_qss())
        self.new_password2.returnPressed.connect(self._on_next)
        self.content_layout.addWidget(self.new_password2)

        self.content_layout.addStretch()

    def _submit_step_3(self):
        p1 = self.new_password.text()
        p2 = self.new_password2.text()
        if p1 != p2:
            self._show_error("Passwords don't match.")
            return
        if len(p1) < 6:
            self._show_error("Password must be at least 6 characters.")
            return

        ok, msg = self.auth.reset_password(self.user_email, self.user_answer, p1)
        if not ok:
            self._show_error(msg)
            return

        from PySide6.QtWidgets import QMessageBox
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

    def _show_error(self, message: str):
        """Show an inline error at the bottom of the content area."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Cannot continue", message)