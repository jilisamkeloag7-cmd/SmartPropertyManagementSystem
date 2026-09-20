print(">>> styles.py V2 <<<")

from PySide6.QtWidgets import QApplication
from ui import theme


def apply_styles(window):
    """Apply global QSS to the application window."""
    qss = f"""
        QMainWindow, QDialog {{
            background-color: {theme.BG_APP};
        }}
        QWidget {{
            font-family: {theme.FONT_FAMILY};
            color: {theme.TEXT_MAIN};
        }}
        QLabel {{
            color: {theme.TEXT_MAIN};
        }}
        QToolTip {{
            background: {theme.TEXT_MAIN};
            color: {theme.TEXT_WHITE};
            border: none;
            padding: 6px 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_SM}px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {theme.BORDER};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {theme.TEXT_FAINT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {theme.BORDER};
            border-radius: 5px;
            min-width: 30px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
    """
    window.setStyleSheet(qss)