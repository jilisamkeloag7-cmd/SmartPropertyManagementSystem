from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Logo/Title
        title = QLabel("🏢 Smart Property Management")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Streamline your property operations with ease")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 18px;
            color: #7f8c8d;
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        # Get Started button
        btn_get_started = QPushButton("Get Started")
        btn_get_started.setFixedSize(220, 55)
        btn_get_started.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 28px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_get_started.clicked.connect(self.parent_window.show_user_type)
        
        # Center the button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_get_started)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)