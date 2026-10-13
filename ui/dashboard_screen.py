
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QFrame, QGridLayout, QMenu,
                                QToolButton, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from Controllers.notification_controller import NotificationController
from Controllers.dashboard_controller import DashboardController
from Controllers.profile_controller import ProfileController
from ui.notification_popup import NotificationPopup
from ui.profile_dialog import ProfileDialog
from ui.widgets.avatar import make_avatar_pixmap
from ui import theme


TILE_W = 170
TILE_H = 90
TILE_GAP = 15

ACTIVITY_COLOURS = {
    "payment": "#10b981",
    "lease": "#3b82f6",
    "maintenance": "#f59e0b",
    "default": "#64748b",
}


class DashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.user_data = None
        self.notif_controller = NotificationController()
        self.dash_controller = DashboardController()
        self.profile_controller = ProfileController()
        self.setup_ui()

    # ------------------------------------------------------------- API
    def set_user(self, user_data):
        self.user_data = user_data
        name  = user_data.get("name", "User")
        role  = user_data.get("role", "User")
        email = user_data.get("email", "")

        self.hero_name.setText(name)
        self.hero_subtitle.setText(f"{role}  ·  {email}")

        self._refresh_avatar()
        self._rebuild_actions()
        self._refresh_notif_count()
        self._refresh_stats()

    # ------------------------------------------------------------- UI
    def setup_ui(self):
        # Outer wrapper with scroll area
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
        layout.setContentsMargins(30, 26, 30, 30)
        layout.setSpacing(20)

        # ---------------- HERO BANNER (replaces old header entirely)
        self.hero_banner = QFrame()
        self.hero_banner.setMinimumHeight(150)
        self.hero_banner.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme.PRIMARY},
                    stop:0.6 {theme.PRIMARY_HOVER},
                    stop:1 {theme.ACCENT_PURPLE});
                border-radius: {theme.RADIUS_XL}px;
                border: none;
            }}
        """)
        hero_layout = QHBoxLayout(self.hero_banner)
        hero_layout.setContentsMargins(28, 22, 22, 22)
        hero_layout.setSpacing(18)

        # Left: greeting text
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        greeting = QLabel("👋  Welcome back")
        greeting.setStyleSheet(
            "color: rgba(255, 255, 255, 210); font-size: 13px; "
            "font-weight: bold; letter-spacing: 0.5px;"
        )
        text_col.addWidget(greeting)

        self.hero_name = QLabel("User")
        self.hero_name.setStyleSheet(
            f"color: {theme.TEXT_WHITE}; font-size: 32px; font-weight: 800;"
        )
        text_col.addWidget(self.hero_name)

        self.hero_subtitle = QLabel("Role  ·  email")
        self.hero_subtitle.setStyleSheet(
            "color: rgba(255, 255, 255, 190); font-size: 13px;"
        )
        text_col.addWidget(self.hero_subtitle)

        text_col.addStretch()
        hero_layout.addLayout(text_col, stretch=1)

        # Right: bell + avatar
        right_col = QHBoxLayout()
        right_col.setSpacing(8)
        right_col.setAlignment(Qt.AlignTop)

        # Bell
        self.bell_container = QWidget()
        self.bell_container.setFixedSize(40, 40)
        self.bell_container.setStyleSheet("background: transparent;")

        self.btn_notif = QPushButton("🔔", self.bell_container)
        self.btn_notif.setGeometry(0, 0, 40, 40)
        self.btn_notif.setCursor(Qt.PointingHandCursor)
        self.btn_notif.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 40);
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 80);
            }
        """)
        self.btn_notif.clicked.connect(self._open_notifications)

        self.badge = QLabel("0", self.bell_container)
        self.badge.setFixedSize(18, 18)
        self.badge.move(24, 0)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setStyleSheet(f"""
            background: {theme.DANGER};
            color: {theme.TEXT_WHITE};
            border-radius: 9px;
            font-size: 10px;
            font-weight: bold;
            border: 2px solid {theme.PRIMARY};
        """)
        self.badge.setVisible(False)

        right_col.addWidget(self.bell_container)

        # Avatar
        self.avatar_btn = QToolButton()
        self.avatar_btn.setCursor(Qt.PointingHandCursor)
        self.avatar_btn.setFixedSize(40, 40)
        self.avatar_btn.setPopupMode(QToolButton.InstantPopup)
        self.avatar_btn.setStyleSheet("""
            QToolButton {
                background: rgba(255, 255, 255, 40);
                border: none;
                border-radius: 20px;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 80);
            }
            QToolButton::menu-indicator { image: none; }
        """)
        self._build_profile_menu()
        right_col.addWidget(self.avatar_btn)

        hero_layout.addLayout(right_col)

        layout.addWidget(self.hero_banner)

        # ---------------- STATS
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        layout.addLayout(self.stats_row)

        # ---------------- QUICK ACTIONS
        quick = QLabel("Quick Actions")
        quick.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(quick)

        self.actions_container = QWidget()
        self.actions_container.setStyleSheet("background: transparent;")
        actions_outer = QHBoxLayout(self.actions_container)
        actions_outer.setContentsMargins(0, 0, 0, 0)
        actions_outer.setSpacing(0)

        actions_outer.addStretch(1)
        self.action_grid = QGridLayout()
        self.action_grid.setSpacing(TILE_GAP)
        self.action_grid.setContentsMargins(0, 0, 0, 0)
        actions_outer.addLayout(self.action_grid)
        actions_outer.addStretch(1)

        layout.addWidget(self.actions_container)

        # ---------------- ACTIVITY + NOTIFICATIONS
        bottom = QHBoxLayout()
        bottom.setSpacing(20)

        self.activity_frame = QFrame()
        self.activity_frame.setMinimumHeight(220)
        self.activity_frame.setStyleSheet(theme.card_qss())
        self.activity_layout = QVBoxLayout(self.activity_frame)
        self.activity_layout.setContentsMargins(18, 16, 18, 16)
        self.activity_layout.setSpacing(8)
        act_title = QLabel("📊 Recent Activity")
        act_title.setMinimumHeight(24)
        act_title.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        self.activity_layout.addWidget(act_title)
        self.activity_layout.addStretch()
        bottom.addWidget(self.activity_frame, stretch=1)

        self.notif_frame = QFrame()
        self.notif_frame.setMinimumHeight(220)
        self.notif_frame.setStyleSheet(theme.card_qss())
        self.notif_layout = QVBoxLayout(self.notif_frame)
        self.notif_layout.setContentsMargins(18, 16, 18, 16)
        self.notif_layout.setSpacing(8)
        notif_title = QLabel("🔔 Upcoming")
        notif_title.setMinimumHeight(24)
        notif_title.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        self.notif_layout.addWidget(notif_title)
        self.notif_layout.addStretch()
        bottom.addWidget(self.notif_frame, stretch=1)

        layout.addLayout(bottom)
        layout.addStretch()

    # ------------------------------------------------------------- profile menu
    def _build_profile_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
                padding: 6px;
                color: {theme.TEXT_MAIN};
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: {theme.RADIUS_SM}px;
                font-size: {theme.FS_BASE}px;
            }}
            QMenu::item:selected {{
                background: {theme.PRIMARY_SOFT};
                color: {theme.PRIMARY};
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme.BORDER};
                margin: 4px 8px;
            }}
        """)

        action_profile = QAction("👤  View Profile", self)
        action_profile.triggered.connect(self._open_profile)
        menu.addAction(action_profile)

        menu.addSeparator()

        action_logout = QAction("🚪  Logout", self)
        action_logout.triggered.connect(self._handle_logout)
        menu.addAction(action_logout)

        self.avatar_btn.setMenu(menu)

    def _refresh_avatar(self):
        if not self.user_data:
            return
        name = self.user_data.get("name", "")
        uid = self.user_data.get("user_id")
        image_path = None
        if uid:
            profile = self.profile_controller.get(uid)
            if profile:
                image_path = profile.get("profile_image_path")
        pix = make_avatar_pixmap(image_path, name, 36)
        self.avatar_btn.setIcon(pix)
        self.avatar_btn.setIconSize(pix.size())

    def _open_profile(self):
        if not self.user_data:
            return
        dlg = ProfileDialog(
            self,
            user_id=self.user_data.get("user_id"),
            session_user=self.user_data,
            on_profile_updated=self._on_profile_updated,
        )
        dlg.exec()

    def _on_profile_updated(self):
        uid = self.user_data.get("user_id")
        if not uid:
            return
        from Repositories.user_repository import UserRepository
        u = UserRepository().find_by_id(uid)
        if not u:
            return
        self.user_data["name"] = u.name
        self.user_data["email"] = u.email
        self.user_data["phone"] = u.phone or ""
        self._refresh_avatar()
        self.hero_name.setText(u.name)
        self.hero_subtitle.setText(f"{u.role.value}  ·  {u.email}")
        self.parent_window.sidebar.set_user(self.user_data)

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
            self.activity_layout.insertWidget(
                self.activity_layout.count() - 1,
                self._make_activity_row(item),
            )

        for item in data.get("upcoming_notifications", []):
            lbl = QLabel(f"• {item}")
            lbl.setMinimumHeight(22)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(
                f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MAIN};"
            )
            self.notif_layout.insertWidget(self.notif_layout.count() - 1, lbl)

    def _make_activity_row(self, text: str):
        lower = text.lower()
        if "payment" in lower:
            colour = ACTIVITY_COLOURS["payment"]
        elif "lease" in lower:
            colour = ACTIVITY_COLOURS["lease"]
        elif "maintenance" in lower or "request" in lower:
            colour = ACTIVITY_COLOURS["maintenance"]
        else:
            colour = ACTIVITY_COLOURS["default"]

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {colour}; font-size: 10px;")
        h.addWidget(dot)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MAIN};"
        )
        h.addWidget(lbl, stretch=1)

        return row

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
        if count > 0:
            self.badge.setText(str(count) if count < 100 else "99+")
            self.badge.setVisible(True)
        else:
            self.badge.setVisible(False)

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
            "Reports":   {"Administrator", "Property Manager", "Owner"},
        }

        pos = 0
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
            self.action_grid.addWidget(b, pos // 2, pos % 2)
            pos += 1

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

