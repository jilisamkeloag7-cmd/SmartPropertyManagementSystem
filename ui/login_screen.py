print(">>> login_screen.py V7 <<<")

import os
import sys

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QBrush
from Controllers.auth_controller import AuthController
from ui import theme


CARD_W = 440


def _assets_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        internal = os.path.join(exe_dir, "_internal")
        base = internal if os.path.isdir(internal) else exe_dir
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Assets")


LOGIN_BG = os.path.join(_assets_dir(), "login_background.jpg")


class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_role = "User"
        self.auth = AuthController()
        self._bg_pixmap = None
        self._load_bg()
        self._build()

    def _load_bg(self):
        if os.path.isfile(LOGIN_BG):
            pix = QPixmap(LOGIN_BG)
            if not pix.isNull():
                self._bg_pixmap = pix

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        if self._bg_pixmap is not None:
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(-x, -y, scaled)

            # Strong overlay so the login card sits cleanly
            if theme.MODE == "dark":
                overlay = QColor(20, 8, 45, 200)
            else:
                overlay = QColor(250, 245, 255, 220)
            painter.fillRect(self.rect(), overlay)
        else:
            # Gradient fallback
            grad = QLinearGradient(0, 0, 0, 1)
            grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            grad.setColorAt(0.0, QColor(theme.BG_GRADIENT_TOP))
            grad.setColorAt(1.0, QColor(theme.BG_GRADIENT_BOTTOM))
            painter.fillRect(self.rect(), QBrush(grad))

        painter.end()

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
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
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
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(14)

        card_layout.addWidget(self._field_label("Email or ID Number"))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. owner@spm.local")
        self.email_input.setFixedHeight(46)
        self.email_input.setStyleSheet(self._input_qss())
        self.email_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.email_input)

        card_layout.addSpacing(2)

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

        card_layout.addSpacing(4)

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

        links_row = QHBoxLayout()
        links_row.setSpacing(8)

        btn_register = QPushButton("Create Account")
        btn_register.setCursor(Qt.PointingHandCursor)
        btn_register.setStyleSheet(self._link_qss())
        btn_register.clicked.connect(self._on_register)
        links_row.addWidget(btn_register)
        links_row.addStretch()

        btn_forgot = QPushButton("Forgot password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.setStyleSheet(self._link_qss())
        btn_forgot.clicked.connect(self._on_forgot_password)
        links_row.addWidget(btn_forgot)

        card_layout.addLayout(links_row)

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
            QPushButton:hover {{ color: {theme.PRIMARY}; }}
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
            f"font-size: {theme.FS_SM}px; font-weight: bold;"
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
            QLineEdit:focus {{ border-color: {theme.PRIMARY}; }}
        """

    @staticmethod
    def _link_qss():
        return f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                font-size: {theme.FS_SM}px;
                padding: 4px 6px;
            }}
            QPushButton:hover {{
                color: {theme.PRIMARY};
                text-decoration: underline;
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

    def _on_register(self):
        from ui.register_dialog import RegisterDialog
        dlg = RegisterDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.auth.register_self(
                data["id_number"], data["name"], data["email"],
                data["phone"], data["password"], data["role_str"],
                data["security_question"], data["security_answer"],
            )
            if ok:
                self.error_label.setStyleSheet(
                    f"color: {theme.SUCCESS_HOVER}; font-size: {theme.FS_SM}px;"
                )
                self.error_label.setText(f"{msg} You can now sign in below.")
                self.email_input.setText(data["email"])
                self.password_input.setFocus()
            else:
                self.error_label.setStyleSheet(
                    f"color: {theme.DANGER}; font-size: {theme.FS_SM}px;"
                )
                self.error_label.setText(msg)

    def _on_forgot_password(self):
        from ui.forgot_password_dialog import ForgotPasswordDialog
        prefill = self.email_input.text().strip()
        dlg = ForgotPasswordDialog(self, prefill_email=prefill)
        if dlg.exec():
            self.error_label.setStyleSheet(
                f"color: {theme.SUCCESS_HOVER}; font-size: {theme.FS_SM}px;"
            )
            self.error_label.setText("Password updated. Please sign in.")

    def handle_login(self):
        identifier = self.email_input.text().strip()
        password   = self.password_input.text()
        self.error_label.setStyleSheet(
            f"color: {theme.DANGER}; font-size: {theme.FS_SM}px;"
        )
        self.error_label.setText("")

        ok, user, err = self.auth.login(identifier, password, self.current_role)
        if not ok:
            self.error_label.setText(err or "Login failed.")
            return

        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.Password)
        self._toggle_btn.setText("Show")

        self.parent_window.show_dashboard(user)