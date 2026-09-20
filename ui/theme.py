print(">>> theme.py V1 <<<")

"""
Central theme constants for the Smart Property Management System.

Design system:
  - Neutral base: slate gray scale
  - Accent: modern blue (#3b82f6)
  - Status colours: emerald / amber / red / sky
  - Spacing scale: multiples of 4
  - Border radii: 6, 10, 14, 20
"""

# ------------------------------------------------------------------ palette
PRIMARY         = "#3b82f6"
PRIMARY_HOVER   = "#2563eb"
PRIMARY_PRESSED = "#1d4ed8"
PRIMARY_SOFT    = "#eff6ff"

# Backgrounds
BG_APP     = "#f1f5f9"
BG_CARD    = "#ffffff"
BG_SUBTLE  = "#f8fafc"

# Text
TEXT_MAIN  = "#0f172a"
TEXT_MUTED = "#64748b"
TEXT_FAINT = "#94a3b8"
TEXT_WHITE = "#ffffff"

# Borders
BORDER       = "#e2e8f0"
BORDER_FOCUS = PRIMARY

# Status
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
def button_qss(kind: str = "primary") -> str:
    """Return QSS for a button of the given kind: primary, secondary, danger,
    success, ghost."""
    styles = {
        "primary":   (PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED, TEXT_WHITE),
        "danger":    (DANGER,  DANGER_HOVER,  "#b91c1c",       TEXT_WHITE),
        "success":   (SUCCESS, SUCCESS_HOVER, "#047857",       TEXT_WHITE),
        "warning":   (WARNING, WARNING_HOVER, "#b45309",       TEXT_WHITE),
        "secondary": (BG_SUBTLE, BORDER,      "#cbd5e1",       TEXT_MAIN),
        "ghost":     ("transparent", BG_SUBTLE, "#e2e8f0",     TEXT_MUTED),
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