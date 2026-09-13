from PySide6.QtWidgets import QApplication

def apply_styles(window):
    """Apply global QSS styles to the application"""
    style = """
    QMainWindow {
        background-color: #f0f4f8;
    }
    QWidget {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    QLabel {
        color: #2c3e50;
    }
    """
    window.setStyleSheet(style)