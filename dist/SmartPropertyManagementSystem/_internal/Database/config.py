print(">>> config.py V2 <<<")

import os
import sys


def _base_dir():
    """Return the folder where the app expects its data files."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle — use the .exe's folder
        return os.path.dirname(sys.executable)
    # Running as a normal Python script — use the project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _base_dir()
DB_PATH = os.path.join(BASE_DIR, "Database", "smartproperty.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

APP_NAME = "Smart Property Management System"
APP_VERSION = "0.1.0"