print(">>> theme.py V2 <<<")

"""
Central theme for the Smart Property Management System.

Mode is picked at import time from QSettings.
Screens import the constants (PRIMARY, BG_APP, ...) and receive
whichever palette corresponds to the current mode.

Restart the app to apply a mode change.
"""

from PySide6.QtCore import QSettings

_ORG = "SPMS"
_APP = "SPMS"

_settings = QSettings(_ORG, _APP)
MODE = _settings.value("theme/mode", "light")   # "light" or "dark"

# ------------------------------------------------------------------ palettes
if MODE == "dark":
    PRIMARY         = "#60a5fa"
    PRIMARY_HOVER   = "#3b82f6"
    PRIMARY_PRESSED = "#2563eb"
    PRIMARY_SOFT    = "#1e3a5f"

    BG_APP     = "#0f172a"
    BG_CARD    = "#1e293b"
    BG_SUBTLE  = "#243449"

    TEXT_MAIN  = "#f1f5f9"
    TEXT_MUTED = "#94a3b8"
    TEXT_FAINT = "#64748b"
    TEXT_WHITE = "#ffffff"

    BORDER       = "#334155"
    BORDER_FOCUS = PRIMARY

    SUCCESS         = "#34d399"
    SUCCESS_HOVER   = "#10b981"
    SUCCESS_SOFT    = "#064e3b"

    WARNING         = "#fbbf24"
    WARNING_HOVER   = "#f59e0b"
    WARNING_SOFT    = "#78350f"

    DANGER          = "#f87171"
    DANGER_HOVER    = "#ef4444"
    DANGER_SOFT     = "#7f1d1d"

    INFO            = "#38bdf8"
    INFO_SOFT       = "#0c4a6e"
else:  # light
    PRIMARY         = "#3b82f6"
    PRIMARY_HOVER   = "#2563eb"
    PRIMARY_PRESSED = "#1d4ed8"
    PRIMARY_SOFT    = "#eff6ff"

    BG_APP     = "#f1f5f9"
    BG_CARD    = "#ffffff"
    BG_SUBTLE  = "#f8fafc"

    TEXT_MAIN  = "#0f172a"
    TEXT_MUTED = "#64748b"
    TEXT_FAINT = "#94a3b8"
    TEXT_WHITE = "#ffffff"

    BORDER       = "#e2e8f0"
    BORDER_FOCUS = PRIMARY

    SUCCESS         = "#10b981"
    SUCCESS_HOVER   = "#059669"
    SUCCESS_SOFT    = "#ecfdf5"

    WARNING         = "#f59e0b"
    WARNING_HOVER   = "#d97706"
    WARNING_SOFT    = "#fffbeb"

    DANGER          = "#ef4444"
    DANGER_HOVER    = "#dc2626"
    DANGER_SOFT     = "#fef2f2"

    INFO            = "#0ea5e9"
    INFO_SOFT       = "#f0f9ff"

# ------------------------------------------------------------------ spacing
SP_1 = 4
SP_2 = 8
SP_3 = 12
SP_4 = 16
SP_5 = 20
SP_6 = 24
SP_8 = 32
SP_10 = 40

# ------------------------------------------------------------------ radii
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14
RADIUS_XL = 20
RADIUS_PILL = 999

# ------------------------------------------------------------------ typography
FS_XS   = 11
FS_SM   = 12
FS_BASE = 13
FS_MD   = 14
FS_LG   = 16
FS_XL   = 20
FS_2XL  = 24
FS_3XL  = 32

FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'


# ------------------------------------------------------------------ helpers
def set_mode(mode: str):
    """Persist the requested mode. Restart to apply."""
    if mode not in ("light", "dark"):
        return
    _settings.setValue("theme/mode", mode)
    _settings.sync()


def toggle_mode() -> str:
    """Flip the mode, save, and return the new mode."""
    new = "light" if MODE == "dark" else "dark"
    set_mode(new)
    return new


def button_qss(kind: str = "primary") -> str:
    styles = {
        "primary":   (PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED, TEXT_WHITE),
        "danger":    (DANGER,  DANGER_HOVER,  DANGER_HOVER,    TEXT_WHITE),
        "success":   (SUCCESS, SUCCESS_HOVER, SUCCESS_HOVER,   TEXT_WHITE),
        "warning":   (WARNING, WARNING_HOVER, WARNING_HOVER,   TEXT_WHITE),
        "secondary": (BG_SUBTLE, BORDER,      BORDER,          TEXT_MAIN),
        "ghost":     ("transparent", BG_SUBTLE, BG_SUBTLE,     TEXT_MUTED),
    }
    bg, hover, pressed, fg = styles.get(kind, styles["primary"])
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: none;
            border-radius: {RADIUS_MD}px;
            font-size: {FS_BASE}px;
            font-weight: bold;
            padding: 8px 18px;
        }}
        QPushButton:hover    {{ background-color: {hover}; }}
        QPushButton:pressed  {{ background-color: {pressed}; }}
        QPushButton:disabled {{ background-color: {BG_SUBTLE}; color: {TEXT_FAINT}; }}
    """


def input_qss() -> str:
    return f"""
        QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {{
            background: {BG_CARD};
            border: 2px solid {BORDER};
            border-radius: {RADIUS_MD}px;
            padding: 8px 12px;
            font-size: {FS_BASE}px;
            color: {TEXT_MAIN};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
        QDateEdit:focus, QSpinBox:focus {{
            border-color: {BORDER_FOCUS};
        }}
    """


def card_qss() -> str:
    return f"""
        QFrame {{
            background: {BG_CARD};
            border-radius: {RADIUS_LG}px;
            border: 1px solid {BORDER};
        }}
    """


def table_qss() -> str:
    return f"""
        QTableWidget {{
            background: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: {RADIUS_LG}px;
            font-size: {FS_BASE}px;
            gridline-color: {BORDER};
        }}
        QHeaderView::section {{
            background: {BG_SUBTLE};
            color: {TEXT_MAIN};
            padding: 10px;
            border: none;
            font-weight: bold;
            font-size: {FS_SM}px;
        }}
        QTableWidget::item {{ padding: 8px; }}
        QTableWidget::item:selected {{
            background: {PRIMARY_SOFT};
            color: {TEXT_MAIN};
        }}
    """


def label_heading_qss() -> str:
    return f"font-size: {FS_2XL}px; font-weight: bold; color: {TEXT_MAIN};"


def label_subtle_qss() -> str:
    return f"font-size: {FS_SM}px; color: {TEXT_MUTED};"

# ------------------------------------------------------------------ pre-login gradients
if MODE == "dark":
    BG_GRADIENT_TOP    = "#1e293b"
    BG_GRADIENT_BOTTOM = "#0f172a"
else:
    BG_GRADIENT_TOP    = "#eff6ff"
    BG_GRADIENT_BOTTOM = "#f8fafc"