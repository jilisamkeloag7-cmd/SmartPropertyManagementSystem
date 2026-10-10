print(">>> theme.py V3 <<<")

"""
Central theme for the Smart Property Management System.

Palette inspired by a neon / synthwave aesthetic:
  Light mode — magenta primary on light lavender
  Dark mode  — deep purple-black with glowing pink + cyan accents

Restart the app to apply a mode change.
"""

from PySide6.QtCore import QSettings

_ORG = "SPMS"
_APP = "SPMS"

_settings = QSettings(_ORG, _APP)
MODE = _settings.value("theme/mode", "light")   # "light" or "dark"


# =====================================================================
# PALETTES
# =====================================================================
if MODE == "dark":
    # Deep purple-black backgrounds with neon accents
    PRIMARY         = "#ec4899"        # hot pink
    PRIMARY_HOVER   = "#f472b6"
    PRIMARY_PRESSED = "#db2777"
    PRIMARY_SOFT    = "#3d1e4a"        # pink-tinted dark

    ACCENT_CYAN     = "#22d3ee"
    ACCENT_PURPLE   = "#a855f7"
    ACCENT_YELLOW   = "#fbbf24"

    BG_APP     = "#170b29"             # deep purple-black
    BG_CARD    = "#231340"
    BG_SUBTLE  = "#2d1a4f"

    TEXT_MAIN  = "#f5f3ff"
    TEXT_MUTED = "#c4b5d4"
    TEXT_FAINT = "#8b6fa8"
    TEXT_WHITE = "#ffffff"

    BORDER       = "#3d2660"
    BORDER_FOCUS = PRIMARY

    SUCCESS         = "#34d399"
    SUCCESS_HOVER   = "#10b981"
    SUCCESS_SOFT    = "#0d3d2e"

    WARNING         = "#fbbf24"
    WARNING_HOVER   = "#f59e0b"
    WARNING_SOFT    = "#3d2a0a"

    DANGER          = "#fb7185"
    DANGER_HOVER    = "#f43f5e"
    DANGER_SOFT     = "#4c0519"

    INFO            = "#22d3ee"
    INFO_SOFT       = "#083344"

    # Gradient for pre-login screens (dark neon look)
    BG_GRADIENT_TOP    = "#1e0b3a"
    BG_GRADIENT_BOTTOM = "#0a0417"
else:
    # Light mode — bright magenta on light lavender
    PRIMARY         = "#db2777"        # magenta
    PRIMARY_HOVER   = "#be185d"
    PRIMARY_PRESSED = "#9d174d"
    PRIMARY_SOFT    = "#fce7f3"        # light pink tint

    ACCENT_CYAN     = "#0891b2"
    ACCENT_PURPLE   = "#7c3aed"
    ACCENT_YELLOW   = "#d97706"

    BG_APP     = "#faf5ff"             # very light lavender
    BG_CARD    = "#ffffff"
    BG_SUBTLE  = "#f5f3ff"

    TEXT_MAIN  = "#1a0b2e"
    TEXT_MUTED = "#6b5a80"
    TEXT_FAINT = "#a99bbf"
    TEXT_WHITE = "#ffffff"

    BORDER       = "#e9d5ff"
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

    INFO            = "#0891b2"
    INFO_SOFT       = "#ecfeff"

    BG_GRADIENT_TOP    = "#fdf4ff"
    BG_GRADIENT_BOTTOM = "#f5f3ff"


# =====================================================================
# SPACING / RADII / TYPOGRAPHY
# =====================================================================
SP_1 = 4
SP_2 = 8
SP_3 = 12
SP_4 = 16
SP_5 = 20
SP_6 = 24
SP_8 = 32
SP_10 = 40

RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14
RADIUS_XL = 20
RADIUS_PILL = 999

FS_XS   = 11
FS_SM   = 12
FS_BASE = 13
FS_MD   = 14
FS_LG   = 16
FS_XL   = 20
FS_2XL  = 24
FS_3XL  = 32
FS_4XL  = 44

FONT_FAMILY = (
    '"Segoe UI Variable Display", "Segoe UI", '
    '-apple-system, BlinkMacSystemFont, Roboto, sans-serif'
)


# =====================================================================
# HELPERS
# =====================================================================
def set_mode(mode: str):
    if mode not in ("light", "dark"):
        return
    _settings.setValue("theme/mode", mode)
    _settings.sync()


def toggle_mode() -> str:
    new = "light" if MODE == "dark" else "dark"
    set_mode(new)
    return new


def button_qss(kind: str = "primary") -> str:
    styles = {
        "primary":   (PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED, TEXT_WHITE),
        "danger":    (DANGER,  DANGER_HOVER,  DANGER_HOVER,    TEXT_WHITE),
        "success":   (SUCCESS, SUCCESS_HOVER, SUCCESS_HOVER,   TEXT_WHITE),
        "warning":   (WARNING, WARNING_HOVER, WARNING_HOVER,   "#1a0b2e"),
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