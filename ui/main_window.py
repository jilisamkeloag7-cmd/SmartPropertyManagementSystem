from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from ui.welcome_screen import WelcomeScreen
from ui.user_type_screen import UserTypeScreen
from ui.login_screen import LoginScreen
from ui.dashboard_screen import DashboardScreen
from ui.properties_screen import PropertiesScreen
from Controllers.auth_controller import AuthController
from ui.styles import apply_styles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Property Management System")
        self.setGeometry(100, 100, 960, 680)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Screens
        self.welcome_screen = WelcomeScreen(self)
        self.user_type_screen = UserTypeScreen(self)
        self.login_screen = LoginScreen(self)
        self.dashboard_screen = DashboardScreen(self)
        self.properties_screen = PropertiesScreen(self)

        # Index map: 0 Welcome, 1 UserType, 2 Login, 3 Dashboard, 4 Properties
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.user_type_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.properties_screen)

        self.stacked_widget.setCurrentIndex(0)
        apply_styles(self)

    # ------------------------------------------------------------------ nav
    def show_user_type(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_login(self, role):
        self.login_screen.set_role(role)
        self.stacked_widget.setCurrentIndex(2)

    def show_dashboard(self, user_data):
        self.dashboard_screen.set_user(user_data)
        self.stacked_widget.setCurrentIndex(3)

    def show_properties(self):
        self.properties_screen.set_user(self.dashboard_screen.user_data)
        self.stacked_widget.setCurrentIndex(4)