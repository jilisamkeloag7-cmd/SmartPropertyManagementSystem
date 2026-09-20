print(">>> login_screen.py V5 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QLinearGradient, QBrush, QColor, QPalette
from Controllers.auth_controller import AuthController
from ui import theme


CARD_W = 440


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_role = "User"
        self.auth = AuthController()
        self._build()

    def set_role(self, role):
        self.clear_fields()
        self.current_role = role
        self.role_label.setText(f"Sign in as {role}")

    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
        self.error_label.setText("")
        self.password_input.setEchoMode(QLineEdit.Password)
        self._toggle_btn.setText("Show")

    def _build(self):
        self.setAutoFillBackground(True)
        pal = self.palette()
        grad = QLinearGradient(0, 0, 0, 1)
        grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QColor(theme.BG_GRADIENT_TOP))
        grad.setColorAt(1.0, QColor(theme.BG_GRADIENT_BOTTOM))
        pal.setBrush(QPalette.Window, QBrush(grad))
        self.setPalette(pal)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        self.role_label = QLabel("Sign in as User")
        self.role_label.setAlignment(Qt.AlignCenter)
        self.role_label.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; "
            f"font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(self.role_label)

        layout.addSpacing(theme.SP_6)

        card = QFrame()
        card.setFixedWidth(CARD_W)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.BG_CARD};
                border-radius: {theme.RADIUS_XL}px;
                border: 1px solid {theme.BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(16)

        card_layout.addWidget(self._field_label("Email or ID Number"))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. owner@spm.local")
        self.email_input.setFixedHeight(46)
        self.email_input.setStyleSheet(self._input_qss())
        self.email_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.email_input)

        card_layout.addSpacing(4)

        pwd_label_row = QHBoxLayout()
        pwd_label_row.addWidget(self._field_label("Password"))
        pwd_label_row.addStretch()

        self._toggle_btn = QPushButton("Show")
        self._toggle_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_btn.setFixedHeight(24)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.PRIMARY};
                border: none;
                font-size: {theme.FS_SM}px;
                font-weight: bold;
                padding: 0 4px;
            }}
            QPushButton:hover {{
                color: {theme.PRIMARY_HOVER};
                text-decoration: underline;
            }}
        """)
        self._toggle_btn.clicked.connect(self._toggle_password)
        pwd_label_row.addWidget(self._toggle_btn)

        card_layout.addLayout(pwd_label_row)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(46)
        self.password_input.setStyleSheet(self._input_qss())
        self.password_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            f"color: {theme.DANGER}; font-size: {theme.FS_SM}px;"
        )
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(30)
        card_layout.addWidget(self.error_label)

        card_layout.addSpacing(6)

        self.btn_signin = QPushButton("Sign In")
        self.btn_signin.setCursor(Qt.PointingHandCursor)
        self.btn_signin.setFixedHeight(50)
        self.btn_signin.setDefault(True)
        self.btn_signin.setAutoDefault(True)
        self.btn_signin.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.PRIMARY};
                color: {theme.TEXT_WHITE};
                border: none;
                border-radius: {theme.RADIUS_MD}px;
                font-size: {theme.FS_LG}px;
                font-weight: bold;
            }}
            QPushButton:hover    {{ background-color: {theme.PRIMARY_HOVER}; }}
            QPushButton:pressed  {{ background-color: {theme.PRIMARY_PRESSED}; }}
        """)
        self.btn_signin.clicked.connect(self.handle_login)
        card_layout.addWidget(self.btn_signin)

        btn_forgot = QPushButton("Forgot password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                font-size: {theme.FS_SM}px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                color: {theme.PRIMARY};
            }}
        """)
        card_layout.addWidget(btn_forgot, alignment=Qt.AlignCenter)

        layout.addWidget(card, alignment=Qt.AlignCenter)

        layout.addSpacing(theme.SP_6)

        back_row = QHBoxLayout()
        back_row.addStretch()

        btn_back = QPushButton("← Back")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setFixedHeight(36)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                font-size: {theme.FS_BASE}px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                color: {theme.PRIMARY};
            }}
        """)
        btn_back.clicked.connect(self._go_back)
        back_row.addWidget(btn_back)
        back_row.addStretch()

        layout.addLayout(back_row)

    @staticmethod
    def _field_label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; "
            f"font-size: {theme.FS_SM}px; "
            f"font-weight: bold;"
        )
        return lbl

    @staticmethod
    def _input_qss():
        return f"""
            QLineEdit {{
                padding: 0 14px;
                border: 2px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
                font-size: {theme.FS_MD}px;
                color: {theme.TEXT_MAIN};
                background: {theme.BG_SUBTLE};
            }}
            QLineEdit:focus {{
                border-color: {theme.PRIMARY};
            }}
        """

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self._toggle_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self._toggle_btn.setText("Show")

    def _go_back(self):
        self.clear_fields()
        self.parent_window._set_screen("user_type")

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
        self._toggle_btn.setText("Show")

        self.parent_window.show_dashboard(user)