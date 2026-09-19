from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt

class UserTypeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)
        
        # Title
        title = QLabel("Who are you?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Select your role to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
        """)
        layout.addWidget(subtitle)
        
        # Role buttons grid
        roles = [
            ("👑", "Administrator"),
            ("📋", "Property Manager"),
            ("🏠", "Owner"),
            ("👤", "Tenant / User")
        ]
        
        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setAlignment(Qt.AlignCenter)
        
        for i, (icon, role) in enumerate(roles):
            btn = QPushButton(f"{icon}\n{role}")
            btn.setFixedSize(170, 110)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #ecf0f1;
                    border-radius: 14px;
                    font-size: 15px;
                    padding: 12px;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #f0f4f8;
                    border-color: #3498db;
                }
            """)
            btn.clicked.connect(lambda checked, r=role: self.parent_window.show_login(r))
            row = i // 2
            col = i % 2
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        
        # Back button
        btn_back = QPushButton("← Back")
        btn_back.setFixedSize(100, 35)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7f8c8d;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #2c3e50;
            }
        """)
        btn_back.clicked.connect(lambda: self.parent_window.stacked_widget.setCurrentIndex(0))
        
        back_layout = QHBoxLayout()
        back_layout.addWidget(btn_back)
        back_layout.addStretch()
        layout.addLayout(back_layout)
        
        self.setLayout(layout)