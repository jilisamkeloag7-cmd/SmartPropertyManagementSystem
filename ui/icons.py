print(">>> icons.py V1 <<<")

"""
Central icon registry.

Currently uses emoji glyphs which render natively on Windows 11.
To migrate to SVG or a font-based icon set, replace the values below
with codepoints or file references and update `icon()` accordingly.
"""

# --- Nav
DASHBOARD     = "🏠"
PROPERTIES    = "🏘"
VIEWINGS      = "📅"
APPLICATIONS  = "📝"
LEASES        = "📄"
PAYMENTS      = "💰"
MAINTENANCE   = "🔧"
OWNERSHIP     = "🔑"
REPORTS       = "📊"
USERS         = "👥"

# --- Actions
ADD           = "+"
EDIT          = "✎"
DELETE        = "✕"
APPROVE       = "✓"
REJECT        = "✕"
LOGOUT        = "→"
THEME_LIGHT   = "☀"
THEME_DARK    = "🌙"
SEARCH        = "🔍"
BELL          = "🔔"
PROFILE       = "👤"
SIGN_IN       = "→"
GUEST         = "👋"

# --- Status
INFO          = "ℹ"
WARNING       = "⚠"
SUCCESS       = "✓"
ERROR         = "✕"


def icon(name: str) -> str:
    """Fetch an icon string by name. Currently returns the emoji."""
    return globals().get(name.upper(), "•")