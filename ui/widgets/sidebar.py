print(">>> sidebar.py V1 <<<")

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QWidget)
from PySide6.QtCore import Qt
from ui import theme


SIDEBAR_W = 220


# Nav items: (icon, label, screen_key)
# `allowed_roles` — None means everyone logged in
NAV_ITEMS = [
    ("🏠", "Dashboard",    "dashboard",    None),
    ("🏘",  "Properties",  "properties",   None),
    ("📄", "Leases",       "leases",       None),
    ("💰", "Payments",     "payments",     None),
    ("🔧", "Maintenance",  "maintenance",  None),
    ("🔑", "Ownership",    "ownerships",   {"Administrator", "Property Manager", "Owner"}),
    ("📊", "Reports",      "reports",      {"Administrator", "Property Manager"}),
    ("👥", "Users",        "users",        {"Administrator"}),
]


class Sidebar(QFrame):
    """
    Persistent left navigation for authenticated screens.
    Calls `on_navigate(screen_key)` when a nav item is clicked.
    """

    def __init__(self, parent=None, on_navigate=None, on_logout=None):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.user_data = None
        self._buttons = {}
        self._active_key = "dashboard"
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self._rebuild_nav_items()

        name = self.user_data.get("name", "User")
        role = self.user_data.get("role", "")
        self.user_name.setText(name)
        self.user_role.setText(role)

    def set_active(self, screen_key: str):
        self._active_key = screen_key
        for key, btn in self._buttons.items():
            if key == screen_key:
                btn.setStyleSheet(self._nav_btn_qss(active=True))
            else:
                btn.setStyleSheet(self._nav_btn_qss(active=False))

    # ------------------------------------------------------------------ UI
    def _build(self):
        self.setFixedWidth(SIDEBAR_W)
        self.setStyleSheet(f"""
            Sidebar {{
                background: {theme.BG_CARD};
                border-right: 1px solid {theme.BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Logo / title
        logo_wrap = QWidget()
        logo_wrap.setStyleSheet(f"background: transparent;")
        logo_layout = QHBoxLayout(logo_wrap)
        logo_layout.setContentsMargins(20, 22, 20, 22)
        logo_layout.setSpacing(10)

        logo_icon = QLabel("🏢")
        logo_icon.setStyleSheet("font-size: 22px;")
        logo_layout.addWidget(logo_icon)

        logo_text = QLabel("Smart Property")
        logo_text.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()

        layout.addWidget(logo_wrap)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {theme.BORDER};")
        layout.addWidget(div)

        # ---- Nav items container
        self.nav_container = QWidget()
        self.nav_container.setStyleSheet("background: transparent;")
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(12, 16, 12, 16)
        self.nav_layout.setSpacing(4)
        self.nav_layout.addStretch()
        layout.addWidget(self.nav_container)

        layout.addStretch()

        # Divider
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet(f"background: {theme.BORDER};")
        layout.addWidget(div2)

        # ---- User info + logout
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 18)
        footer_layout.setSpacing(4)

        self.user_name = QLabel("User")
        self.user_name.setStyleSheet(
            f"font-size: {theme.FS_BASE}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        footer_layout.addWidget(self.user_name)

        self.user_role = QLabel("")
        self.user_role.setStyleSheet(
            f"font-size: {theme.FS_XS}px; color: {theme.TEXT_MUTED};"
        )
        footer_layout.addWidget(self.user_role)

        footer_layout.addSpacing(10)

        btn_logout = QPushButton("Logout")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setFixedHeight(34)
        btn_logout.setStyleSheet(theme.button_qss("danger"))
        btn_logout.clicked.connect(self._handle_logout)
        footer_layout.addWidget(btn_logout)

        layout.addWidget(footer)

    # ------------------------------------------------------------------ nav
    def _rebuild_nav_items(self):
        # Clear existing items
        while self.nav_layout.count() > 1:  # keep trailing stretch
            item = self.nav_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._buttons = {}

        role = (self.user_data or {}).get("role", "")

        for icon, label, key, allowed in NAV_ITEMS:
            if allowed is not None and role not in allowed:
                continue
            btn = self._make_nav_button(icon, label, key)
            self.nav_layout.insertWidget(self.nav_layout.count() - 1, btn)
            self._buttons[key] = btn

        # Apply active state
        self.set_active(self._active_key)

    def _make_nav_button(self, icon, label, key):
        btn = QPushButton(f"  {icon}   {label}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet(self._nav_btn_qss(active=False))
        btn.clicked.connect(lambda checked=False, k=key: self._on_click(k))
        return btn

    @staticmethod
    def _nav_btn_qss(active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background: {theme.PRIMARY_SOFT};
                    color: {theme.PRIMARY};
                    border: none;
                    border-radius: {theme.RADIUS_MD}px;
                    font-size: {theme.FS_BASE}px;
                    font-weight: bold;
                    text-align: left;
                    padding: 0 12px;
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                color: {theme.TEXT_MUTED};
                border: none;
                border-radius: {theme.RADIUS_MD}px;
                font-size: {theme.FS_BASE}px;
                text-align: left;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {theme.BG_SUBTLE};
                color: {theme.TEXT_MAIN};
            }}
        """

    def _on_click(self, key):
        self.set_active(key)
        if self.on_navigate:
            self.on_navigate(key)

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()