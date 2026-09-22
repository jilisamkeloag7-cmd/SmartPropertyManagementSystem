print(">>> styles.py V3 <<<")

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

        /* ---- Calendar popup (QDateEdit) — force light so dates are always readable */
        QCalendarWidget QWidget {{
            alternate-background-color: #ffffff;
        }}
        QCalendarWidget QAbstractItemView:enabled {{
            color: #0f172a;
            background-color: #ffffff;
            selection-background-color: #3b82f6;
            selection-color: #ffffff;
            outline: 0;
        }}
        QCalendarWidget QAbstractItemView:disabled {{
            color: #cbd5e1;
        }}
        QCalendarWidget QToolButton {{
            color: #0f172a;
            background-color: transparent;
            border: none;
            padding: 4px 8px;
            font-size: 13px;
            font-weight: bold;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: #eff6ff;
            border-radius: 4px;
        }}
        QCalendarWidget QMenu {{
            background-color: #ffffff;
            color: #0f172a;
        }}
        QCalendarWidget QMenu::item:selected {{
            background-color: #3b82f6;
            color: #ffffff;
        }}
        QCalendarWidget QSpinBox {{
            color: #0f172a;
            background-color: #ffffff;
            selection-background-color: #3b82f6;
            selection-color: #ffffff;
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: #f8fafc;
        }}
    """
    window.setStyleSheet(qss)