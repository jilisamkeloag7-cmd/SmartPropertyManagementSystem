print(">>> dashboard_screen.py V11 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFrame, QGridLayout)
from PySide6.QtCore import Qt
from Controllers.notification_controller import NotificationController
from Controllers.dashboard_controller import DashboardController
from ui.notification_popup import NotificationPopup


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.user_data = None
        self.notif_controller = NotificationController()
        self.dash_controller = DashboardController()
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
        self._refresh_notif_count()
        self._refresh_stats()

    # ------------------------------------------------------------- UI
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

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

        self.btn_notif = QPushButton("🔔 0")
        self.btn_notif.setStyleSheet(
            "background: transparent; border: none; font-size: 16px; padding: 5px 10px;"
        )
        self.btn_notif.setCursor(Qt.PointingHandCursor)
        self.btn_notif.clicked.connect(self._open_notifications)
        header.addWidget(self.btn_notif)

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

        layout.addSpacing(10)
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        layout.addLayout(self.stats_row)

        layout.addSpacing(10)
        quick = QLabel("Quick Actions")
        quick.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(quick)

        self.action_grid = QGridLayout()
        self.action_grid.setSpacing(15)
        layout.addLayout(self.action_grid)

        layout.addSpacing(20)
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        self.activity_frame = QFrame()
        self.activity_frame.setMinimumHeight(200)
        self.activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
            }
        """)
        self.activity_layout = QVBoxLayout(self.activity_frame)
        self.activity_layout.setContentsMargins(18, 16, 18, 16)
        self.activity_layout.setSpacing(8)
        act_title = QLabel("📊 Recent Activity")
        act_title.setMinimumHeight(24)
        act_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
        )
        self.activity_layout.addWidget(act_title)
        self.activity_layout.addStretch()
        bottom.addWidget(self.activity_frame, stretch=1)

        self.notif_frame = QFrame()
        self.notif_frame.setMinimumHeight(200)
        self.notif_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
            }
        """)
        self.notif_layout = QVBoxLayout(self.notif_frame)
        self.notif_layout.setContentsMargins(18, 16, 18, 16)
        self.notif_layout.setSpacing(8)
        notif_title = QLabel("🔔 Upcoming")
        notif_title.setMinimumHeight(24)
        notif_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
        )
        self.notif_layout.addWidget(notif_title)
        self.notif_layout.addStretch()
        bottom.addWidget(self.notif_frame, stretch=1)

        layout.addLayout(bottom)
        self.setLayout(layout)

    # ------------------------------------------------------------- stats refresh
    def _refresh_stats(self):
        if not self.user_data:
            return

        while self.stats_row.count():
            item = self.stats_row.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._clear_list_layout(self.activity_layout)
        self._clear_list_layout(self.notif_layout)

        try:
            data = self.dash_controller.aggregate_for(self.user_data)
        except Exception as e:
            print(f"[dashboard] aggregation failed: {e}")
            return

        for stat in data.get("stats", []):
            card = QFrame()
            card.setFixedHeight(82)
            card.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 12px;
                    border: 1px solid #ecf0f1;
                }
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(2)

            val = QLabel(str(stat["value"]))
            val.setMinimumHeight(28)
            val.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #2c3e50;"
            )
            cl.addWidget(val)

            lbl = QLabel(stat["label"])
            lbl.setMinimumHeight(16)
            lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            cl.addWidget(lbl)

            self.stats_row.addWidget(card, stretch=1)

        for item in data.get("recent_activity", []):
            lbl = QLabel(f"• {item}")
            lbl.setMinimumHeight(22)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; color: #2c3e50;")
            self.activity_layout.insertWidget(
                self.activity_layout.count() - 1, lbl
            )

        for item in data.get("upcoming_notifications", []):
            lbl = QLabel(f"• {item}")
            lbl.setMinimumHeight(22)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; color: #2c3e50;")
            self.notif_layout.insertWidget(
                self.notif_layout.count() - 1, lbl
            )

    @staticmethod
    def _clear_list_layout(layout):
        while layout.count() > 2:
            item = layout.takeAt(1)
            w = item.widget()
            if w:
                w.deleteLater()

    # ------------------------------------------------------------- notifications
    def _refresh_notif_count(self):
        if not self.user_data:
            return
        uid = self.user_data.get("user_id")
        if not uid:
            return
        try:
            count = self.notif_controller.unread_count(uid)
        except Exception as e:
            print(f"[dashboard] notif count failed: {e}")
            count = 0
        self.btn_notif.setText(f"🔔 {count}")

    def _open_notifications(self):
        if not self.user_data:
            return
        dlg = NotificationPopup(
            self,
            controller=self.notif_controller,
            user_id=self.user_data.get("user_id"),
            on_close_callback=self._refresh_notif_count,
        )
        dlg.exec()
        self._refresh_notif_count()

    # ------------------------------------------------------------- actions grid
    def _rebuild_actions(self):
        while self.action_grid.count():
            item = self.action_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        actions = [
            ("🏠", "Properties",  self._open_properties,  None),
            ("📄", "Leases",      self._open_leases,      None),
            ("💰", "Payments",    self._open_payments,    None),
            ("🔧", "Maintenance", self._open_maintenance, None),
            ("🔑", "Ownership",   self._open_ownerships,  "Owner"),
            ("📊", "Reports",     self._open_reports,     "Manager"),
            ("👥", "Users",       self._open_users,       "Administrator"),
        ]

        current_role = (self.user_data or {}).get("role", "")
        role_overrides = {
            "Ownership": {"Administrator", "Property Manager", "Owner"},
            "Reports":   {"Administrator", "Property Manager"},
        }

        pos = 0
        for icon, label, handler, required_role in actions:
            if required_role:
                allowed = role_overrides.get(label, {required_role})
                if current_role not in allowed:
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

    def _open_leases(self):
        self.parent_window.show_leases()

    def _open_payments(self):
        self.parent_window.show_payments()

    def _open_maintenance(self):
        self.parent_window.show_maintenance()

    def _open_ownerships(self):
        self.parent_window.show_ownerships()

    def _open_reports(self):
        self.parent_window.show_reports()

    def _open_users(self):
        self.parent_window.show_users()