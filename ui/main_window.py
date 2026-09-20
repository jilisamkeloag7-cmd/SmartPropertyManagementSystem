print(">>> main_window.py V9 <<<")

from PySide6.QtWidgets import (QMainWindow, QStackedWidget, QVBoxLayout,
                                QHBoxLayout, QWidget, QGraphicsOpacityEffect)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from ui.welcome_screen import WelcomeScreen
from ui.user_type_screen import UserTypeScreen
from ui.login_screen import LoginScreen
from ui.dashboard_screen import DashboardScreen
from ui.properties_screen import PropertiesScreen
from ui.users_screen import UsersScreen
from ui.leases_screen import LeasesScreen
from ui.payments_screen import PaymentsScreen
from ui.maintenance_screen import MaintenanceScreen
from ui.ownerships_screen import OwnershipsScreen
from ui.reports_screen import ReportsScreen
from ui.widgets.sidebar import Sidebar
from ui.styles import apply_styles


SCREENS = {
    "welcome":     0,
    "user_type":   1,
    "login":       2,
    "dashboard":   3,
    "properties":  4,
    "users":       5,
    "leases":      6,
    "payments":    7,
    "maintenance": 8,
    "ownerships":  9,
    "reports":     10,
}

AUTHENTICATED_SCREENS = {
    "dashboard", "properties", "users", "leases",
    "payments", "maintenance", "ownerships", "reports",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Property Management System")
        self.setGeometry(100, 100, 1100, 720)

        self._anim = None   # keep reference so Qt doesn't GC the animation

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self._on_sidebar_navigate,
            on_logout=self._on_sidebar_logout,
        )
        self.sidebar.setVisible(False)
        root.addWidget(self.sidebar)

        # ---- Stacked content
        self.stacked_widget = QStackedWidget()
        root.addWidget(self.stacked_widget, stretch=1)

        # ---- Screens
        self.welcome_screen     = WelcomeScreen(self)
        self.user_type_screen   = UserTypeScreen(self)
        self.login_screen       = LoginScreen(self)
        self.dashboard_screen   = DashboardScreen(self)
        self.properties_screen  = PropertiesScreen(self)
        self.users_screen       = UsersScreen(self)
        self.leases_screen      = LeasesScreen(self)
        self.payments_screen    = PaymentsScreen(self)
        self.maintenance_screen = MaintenanceScreen(self)
        self.ownerships_screen  = OwnershipsScreen(self)
        self.reports_screen     = ReportsScreen(self)

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.user_type_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.properties_screen)
        self.stacked_widget.addWidget(self.users_screen)
        self.stacked_widget.addWidget(self.leases_screen)
        self.stacked_widget.addWidget(self.payments_screen)
        self.stacked_widget.addWidget(self.maintenance_screen)
        self.stacked_widget.addWidget(self.ownerships_screen)
        self.stacked_widget.addWidget(self.reports_screen)

        self.stacked_widget.setCurrentIndex(0)
        apply_styles(self)

    # ------------------------------------------------------------------ transition
    def _animate_transition(self):
        """Fade the current widget in. Safe to call on every screen change."""
        current = self.stacked_widget.currentWidget()
        if current is None:
            return

        # Cancel any animation still running
        if self._anim is not None:
            try:
                self._anim.stop()
            except RuntimeError:
                pass

        effect = QGraphicsOpacityEffect(current)
        current.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def _cleanup():
            try:
                current.setGraphicsEffect(None)
            except RuntimeError:
                pass

        anim.finished.connect(_cleanup)
        self._anim = anim
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # ------------------------------------------------------------------ nav
    def _set_screen(self, key: str):
        idx = SCREENS.get(key)
        if idx is None:
            return

        # Skip animation for the very first screen (startup)
        if self.stacked_widget.currentIndex() == idx and self.stacked_widget.isVisible():
            return

        self.stacked_widget.setCurrentIndex(idx)

        if key in AUTHENTICATED_SCREENS:
            self.sidebar.setVisible(True)
            self.sidebar.set_active(key)
        else:
            self.sidebar.setVisible(False)

        self._animate_transition()

    def show_user_type(self):
        self._set_screen("user_type")

    def show_login(self, role):
        self.login_screen.set_role(role)
        self._set_screen("login")

    def show_dashboard(self, user_data):
        self.dashboard_screen.set_user(user_data)
        self.sidebar.set_user(user_data)
        self.sidebar.setVisible(True)
        self._set_screen("dashboard")

    def show_properties(self):
        self.properties_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("properties")

    def show_users(self):
        self.users_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("users")

    def show_leases(self):
        self.leases_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("leases")

    def show_payments(self):
        self.payments_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("payments")

    def show_maintenance(self):
        self.maintenance_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("maintenance")

    def show_ownerships(self):
        self.ownerships_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("ownerships")

    def show_reports(self):
        self.reports_screen.set_user(self.dashboard_screen.user_data)
        self._set_screen("reports")

    # ------------------------------------------------------------------ sidebar hooks
    def _on_sidebar_navigate(self, key: str):
        user = self.dashboard_screen.user_data
        if not user:
            return

        navigators = {
            "dashboard":   lambda: self.show_dashboard(user),
            "properties":  self.show_properties,
            "leases":      self.show_leases,
            "payments":    self.show_payments,
            "maintenance": self.show_maintenance,
            "ownerships":  self.show_ownerships,
            "reports":     self.show_reports,
            "users":       self.show_users,
        }
        fn = navigators.get(key)
        if fn:
            fn()

    def _on_sidebar_logout(self):
        self.sidebar.setVisible(False)
        self.login_screen.clear_fields()
        self._set_screen("welcome")