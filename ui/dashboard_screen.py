print(">>> dashboard_screen.py V3 <<<")

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

    # ------------------------------------------------------------- UI
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # ---------------- Header
        header = QHBoxLayout()

        title = QLabel("🏢 Smart Property Management")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50;"
        )
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

        # ---- Logout button (created BEFORE connecting)
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
        btn_logout.clicked.connect(self._handle_logout)   # connect AFTER creation
        header.addWidget(btn_logout)

        layout.addLayout(header)

        # ---------------- Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(sep)

        # ---------------- Role line
        self.role_label = QLabel("Role: User")
        self.role_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(self.role_label)

        # ---------------- Quick Actions
        layout.addSpacing(20)
        quick = QLabel("Quick Actions")
        quick.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(quick)

        action_grid = QGridLayout()
        action_grid.setSpacing(15)

        actions = [
            ("🏠", "Properties"),
            ("📄", "Leases"),
            ("💰", "Payments"),
            ("🔧", "Maintenance"),
        ]
        for i, (icon, label) in enumerate(actions):
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
            action_grid.addWidget(b, i // 2, i % 2)

        layout.addLayout(action_grid)

        # ---------------- Activity + Notifications
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

    # ------------------------------------------------------------- handlers
    def _handle_logout(self):
        self.user_data = None
        self.parent_window.login_screen.clear_fields()
        self.parent_window.stacked_widget.setCurrentIndex(0)