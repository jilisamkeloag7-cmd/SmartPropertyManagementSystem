print(">>> dashboard_screen.py V4 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFrame, QGridLayout)
from PySide6.QtCore import Qt


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.user_data = None
        self.setup_ui()

    # ------------------------------------------------------------- API
    def set_user(self, user_data):
        self.user_data = user_data
        name  = user_data.get("name", "User")
        role  = user_data.get("role", "User")
        email = user_data.get("email", "")
        self.welcome_label.setText(f"Welcome back, {name}")
        self.role_label.setText(f"Role: {role}  •  {email}")
        self._rebuild_actions()

    # ------------------------------------------------------------- UI
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QHBoxLayout()

        title = QLabel("🏢 Smart Property Management")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()

        self.welcome_label = QLabel("Welcome back, User")
        self.welcome_label.setStyleSheet(
            "color: #2c3e50; font-size: 14px; font-weight: bold;"
        )
        header.addWidget(self.welcome_label)

        btn_notif = QPushButton("🔔 3")
        btn_notif.setStyleSheet(
            "background: transparent; border: none; font-size: 16px; padding: 5px 10px;"
        )
        header.addWidget(btn_notif)

        btn_profile = QPushButton("👤")
        btn_profile.setStyleSheet(
            "background: transparent; border: none; font-size: 16px; padding: 5px 10px;"
        )
        header.addWidget(btn_profile)

        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_logout.clicked.connect(self._handle_logout)
        header.addWidget(btn_logout)

        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(sep)

        self.role_label = QLabel("Role: User")
        self.role_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(self.role_label)

        layout.addSpacing(20)
        quick = QLabel("Quick Actions")
        quick.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(quick)

        self.action_grid = QGridLayout()
        self.action_grid.setSpacing(15)
        layout.addLayout(self.action_grid)

        layout.addSpacing(30)
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
                padding: 15px;
            }
        """)
        al = QVBoxLayout(activity_frame)
        al.addWidget(QLabel("📊 Recent Activity"))
        al.addWidget(QLabel("• Property #101 viewed"))
        al.addWidget(QLabel("• Lease renewed"))
        al.addWidget(QLabel("• Payment received"))
        bottom.addWidget(activity_frame)

        notif_frame = QFrame()
        notif_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
                padding: 15px;
            }
        """)
        nl = QVBoxLayout(notif_frame)
        nl.addWidget(QLabel("🔔 Notifications"))
        nl.addWidget(QLabel("⚠️ Rent due soon"))
        nl.addWidget(QLabel("✅ Repair updated"))
        bottom.addWidget(notif_frame)

        layout.addLayout(bottom)
        self.setLayout(layout)

    # ------------------------------------------------------------- actions grid
    def _rebuild_actions(self):
        while self.action_grid.count():
            item = self.action_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        actions = [
            ("🏠", "Properties",  self._open_properties, None),
            ("📄", "Leases",      self._open_leases,     None),
            ("👥", "Users",       self._open_users,      "Administrator"),
            ("💰", "Payments",    None,                  None),
            ("🔧", "Maintenance", None,                  None),
        ]

        current_role = (self.user_data or {}).get("role", "")
        pos = 0
        for icon, label, handler, required_role in actions:
            if required_role and current_role != required_role:
                continue
            b = QPushButton(f"{icon}\n{label}")
            b.setFixedSize(170, 90)
            b.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #ecf0f1;
                    border-radius: 12px;
                    font-size: 15px;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    border-color: #3498db;
                }
            """)
            if handler:
                b.clicked.connect(handler)
            else:
                b.setEnabled(False)
                b.setToolTip("Coming soon")
            self.action_grid.addWidget(b, pos // 2, pos % 2)
            pos += 1

    # ------------------------------------------------------------- handlers
    def _handle_logout(self):
        self.user_data = None
        self.parent_window.login_screen.clear_fields()
        self.parent_window.stacked_widget.setCurrentIndex(0)

    def _open_properties(self):
        self.parent_window.show_properties()

    def _open_users(self):
        self.parent_window.show_users()

    def _open_leases(self):
        self.parent_window.show_leases()    