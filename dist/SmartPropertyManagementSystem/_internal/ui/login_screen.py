print(">>> login_screen.py V3 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Qt
from Controllers.auth_controller import AuthController


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_role = "User"
        self.auth = AuthController()
        self.setup_ui()

    def set_role(self, role):
        self.clear_fields()
        self.current_role = role
        self.role_label.setText(f"Sign in as {role}")

    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
        self.error_label.setText("")
        self.password_input.setEchoMode(QLineEdit.Password)
        self._toggle_label.setText("Show")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)

        self.role_label = QLabel("Sign in as User")
        self.role_label.setAlignment(Qt.AlignCenter)
        self.role_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(self.role_label)

        card = QFrame()
        card.setFixedSize(460, 460)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #ecf0f1;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(35, 40, 35, 40)

        # Email / ID
        card_layout.addWidget(self._label("Email or ID Number"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. owner@spm.local")
        self.email_input.setFixedHeight(46)
        self.email_input.setStyleSheet(self._input_style())
        self.email_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.email_input)

        # Password label
        card_layout.addWidget(self._label("Password"))

        # Password row: input + Show/Hide label
        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(46)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self.handle_login)
        pwd_row.addWidget(self.password_input, stretch=1)

        self._toggle_label = QLabel("Show")
        self._toggle_label.setAlignment(Qt.AlignCenter)
        self._toggle_label.setFixedSize(60, 46)
        self._toggle_label.setCursor(Qt.PointingHandCursor)
        self._toggle_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 13px;
                font-weight: bold;
                background-color: #f8fbfe;
                border: 2px solid #d6e6f3;
                border-radius: 10px;
            }
            QLabel:hover {
                background-color: #eaf3fb;
                border-color: #3498db;
            }
        """)
        self._toggle_label.mousePressEvent = self._on_toggle_click
        pwd_row.addWidget(self._toggle_label, stretch=0)

        card_layout.addLayout(pwd_row)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(28)
        card_layout.addWidget(self.error_label)

        # Sign In button
        self.btn_signin = QPushButton("Sign In")
        self.btn_signin.setFixedHeight(48)
        self.btn_signin.setDefault(True)
        self.btn_signin.setAutoDefault(True)
        self.btn_signin.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                border: none; border-radius: 10px;
                font-size: 16px; font-weight: bold;
            }
            QPushButton:hover   { background-color: #2980b9; }
            QPushButton:pressed { background-color: #2471a3; }
        """)
        self.btn_signin.clicked.connect(self.handle_login)
        card_layout.addWidget(self.btn_signin)

        btn_forgot = QPushButton("Forgot password?")
        btn_forgot.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; font-size: 13px;"
        )
        card_layout.addWidget(btn_forgot, alignment=Qt.AlignCenter)

        layout.addWidget(card, alignment=Qt.AlignCenter)

        # Back
        btn_back = QPushButton("← Back")
        btn_back.setFixedSize(100, 35)
        btn_back.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; font-size: 14px;"
        )
        btn_back.clicked.connect(self._go_back)
        back_layout = QHBoxLayout()
        back_layout.addWidget(btn_back)
        back_layout.addStretch()
        layout.addLayout(back_layout)

        self.setLayout(layout)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #7f8c8d; font-size: 13px; font-weight: bold;")
        return lbl

    @staticmethod
    def _input_style():
        return """
            QLineEdit {
                padding: 0 12px;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                font-size: 14px;
                color: #2c3e50;
                background: white;
            }
            QLineEdit:focus { border-color: #3498db; }
        """

    def _on_toggle_click(self, event):
        self._toggle_password()

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self._toggle_label.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self._toggle_label.setText("Show")

    def _go_back(self):
        self.clear_fields()
        self.parent_window.stacked_widget.setCurrentIndex(1)

    def handle_login(self):
        identifier = self.email_input.text().strip()
        password   = self.password_input.text()
        self.error_label.setText("")

        ok, user, err = self.auth.login(identifier, password, self.current_role)
        if not ok:
            self.error_label.setText(err or "Login failed.")
            return

        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.Password)
        self._toggle_label.setText("Show")

        self.parent_window.show_dashboard(user)