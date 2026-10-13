
from PySide6.QtWidgets import QApplication
from ui import theme


def apply_styles(window):
    qss = f"""
        QMainWindow, QDialog {{
            background-color: {theme.BG_APP};
        }}
        QHeaderView::section {{
            padding: 8px 10px;
        }}
        QWidget {{
            font-family: {theme.FONT_FAMILY};
            color: {theme.TEXT_MAIN};
        }}
        QLabel {{
            color: {theme.TEXT_MAIN};
            background: transparent;
        }}
        QToolTip {{
            background: {theme.TEXT_MAIN};
            color: {theme.BG_CARD};
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

        /* ---- Calendar popup — force light so dates are always readable */
        QCalendarWidget QWidget {{
            alternate-background-color: #ffffff;
        }}
        QCalendarWidget QAbstractItemView:enabled {{
            color: #1a0b2e;
            background-color: #ffffff;
            selection-background-color: {theme.PRIMARY};
            selection-color: #ffffff;
            outline: 0;
        }}
        QCalendarWidget QAbstractItemView:disabled {{
            color: #cbd5e1;
        }}
        QCalendarWidget QToolButton {{
            color: #1a0b2e;
            background-color: transparent;
            border: none;
            padding: 4px 8px;
            font-size: 13px;
            font-weight: bold;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: #fce7f3;
            border-radius: 4px;
        }}
        QCalendarWidget QMenu {{
            background-color: #ffffff;
            color: #1a0b2e;
        }}
        QCalendarWidget QMenu::item:selected {{
            background-color: {theme.PRIMARY};
            color: #ffffff;
        }}
        QCalendarWidget QSpinBox {{
            color: #1a0b2e;
            background-color: #ffffff;
            selection-background-color: {theme.PRIMARY};
            selection-color: #ffffff;
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: #faf5ff;
        }}
    """
    window.setStyleSheet(qss)
