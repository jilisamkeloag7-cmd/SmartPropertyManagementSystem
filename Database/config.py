print(">>> config.py V5 <<<")

import os
import sys


def _base_dir():
    """Return the folder where the app expects its data files."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        # PyInstaller 6.x --onedir layout puts bundled data under _internal/
        internal = os.path.join(exe_dir, "_internal")
        if os.path.isdir(internal):
            return internal
        return exe_dir
    # Normal script mode — project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _base_dir()
DB_PATH = os.path.join(BASE_DIR, "Database", "smartproperty.db")

DATABASE_URL = os.environ.get("SPMS_DATABASE_URL", f"sqlite:///{DB_PATH}")

APP_NAME = "Smart Property Management System"
APP_VERSION = "0.1.0"