print(">>> dashboard_screen.py V13 <<<")

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt
from Controllers.notification_controller import NotificationController
from Controllers.dashboard_controller import DashboardController
from ui.notification_popup import NotificationPopup
from ui import theme


TILE_W = 170
TILE_H = 90
TILE_GAP = 15


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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {theme.BG_APP};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # ============================================================
        # HEADER
        # ============================================================
        header = QHBoxLayout()

        title = QLabel("🏢 Smart Property Management")
        title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
        header.addStretch()

        self.welcome_label = QLabel("Welcome back, User")
        self.welcome_label.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_MD}px; "
            f"font-weight: bold;"
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
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet(theme.button_qss("danger"))
        btn_logout.clicked.connect(self._handle_logout)
        header.addWidget(btn_logout)

        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {theme.BORDER}; max-height: 1px;")
        layout.addWidget(sep)

        self.role_label = QLabel("Role: User")
        self.role_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_MD}px;"
        )
        layout.addWidget(self.role_label)

        # ============================================================
        # STATS ROW
        # ============================================================
        layout.addSpacing(8)
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        layout.addLayout(self.stats_row)

        # ============================================================
        # QUICK ACTIONS
        # ============================================================
        layout.addSpacing(8)
        quick = QLabel("Quick Actions")
        quick.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(quick)

        # Container wraps the grid so we can enforce a min height AND
        # horizontally center the grid within the full window width.
        self.actions_container = QWidget()
        container_layout = QHBoxLayout(self.actions_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        container_layout.addStretch(1)   # left flexible spacer

        self.action_grid = QGridLayout()
        self.action_grid.setSpacing(TILE_GAP)
        self.action_grid.setContentsMargins(0, 0, 0, 0)
        container_layout.addLayout(self.action_grid)

        container_layout.addStretch(1)   # right flexible spacer

        layout.addWidget(self.actions_container)

        # ============================================================
        # BOTTOM PANELS
        # ============================================================
        layout.addSpacing(12)
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        self.activity_frame = QFrame()
        self.activity_frame.setMinimumHeight(180)
        self.activity_frame.setStyleSheet(theme.card_qss())
        self.activity_layout = QVBoxLayout(self.activity_frame)
        self.activity_layout.setContentsMargins(18, 16, 18, 16)
        self.activity_layout.setSpacing(8)
        act_title = QLabel("📊 Recent Activity")
        act_title.setMinimumHeight(24)
        act_title.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        self.activity_layout.addWidget(act_title)
        self.activity_layout.addStretch()
        bottom.addWidget(self.activity_frame, stretch=1)

        self.notif_frame = QFrame()
        self.notif_frame.setMinimumHeight(180)
        self.notif_frame.setStyleSheet(theme.card_qss())
        self.notif_layout = QVBoxLayout(self.notif_frame)
        self.notif_layout.setContentsMargins(18, 16, 18, 16)
        self.notif_layout.setSpacing(8)
        notif_title = QLabel("🔔 Upcoming")
        notif_title.setMinimumHeight(24)
        notif_title.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        self.notif_layout.addWidget(notif_title)
        self.notif_layout.addStretch()
        bottom.addWidget(self.notif_frame, stretch=1)

        layout.addLayout(bottom, stretch=1)

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
            card.setStyleSheet(theme.card_qss())
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(2)

            val = QLabel(str(stat["value"]))
            val.setMinimumHeight(28)
            val.setStyleSheet(
                f"font-size: {theme.FS_2XL}px; font-weight: bold; "
                f"color: {theme.TEXT_MAIN};"
            )
            cl.addWidget(val)

            lbl = QLabel(stat["label"])
            lbl.setMinimumHeight(16)
            lbl.setStyleSheet(
                f"font-size: {theme.FS_XS}px; color: {theme.TEXT_MUTED};"
            )
            cl.addWidget(lbl)

            self.stats_row.addWidget(card, stretch=1)

        for item in data.get("recent_activity", []):
            lbl = QLabel(f"• {item}")
            lbl.setMinimumHeight(22)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(
                f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MAIN};"
            )
            self.activity_layout.insertWidget(
                self.activity_layout.count() - 1, lbl
            )

        for item in data.get("upcoming_notifications", []):
            lbl = QLabel(f"• {item}")
            lbl.setMinimumHeight(22)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(
                f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MAIN};"
            )
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
        rows_used = 0
        cols_per_row = 2

        for icon, label, handler, required_role in actions:
            if required_role:
                allowed = role_overrides.get(label, {required_role})
                if current_role not in allowed:
                    continue

            b = QPushButton(f"{icon}\n{label}")
            b.setFixedSize(TILE_W, TILE_H)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.BG_CARD};
                    border: 2px solid {theme.BORDER};
                    border-radius: {theme.RADIUS_LG}px;
                    font-size: {theme.FS_MD}px;
                    color: {theme.TEXT_MAIN};
                }}
                QPushButton:hover {{
                    background-color: {theme.PRIMARY_SOFT};
                    border-color: {theme.PRIMARY};
                }}
            """)
            if handler:
                b.clicked.connect(handler)
            else:
                b.setEnabled(False)
                b.setToolTip("Coming soon")
            row = pos // cols_per_row
            col = pos % cols_per_row
            self.action_grid.addWidget(b, row, col)
            rows_used = max(rows_used, row + 1)
            pos += 1

        # Reserve enough vertical space so the bottom panels can't squish the tiles
        needed_height = (
            rows_used * TILE_H + max(0, rows_used - 1) * TILE_GAP
        )
        self.actions_container.setMinimumHeight(needed_height)

    # ------------------------------------------------------------- handlers
    def _handle_logout(self):
        self.user_data = None
        self.parent_window._on_sidebar_logout()

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