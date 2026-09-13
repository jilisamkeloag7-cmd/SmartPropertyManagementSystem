import os

# Project root (one level up from Database/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite database file location
DB_PATH = os.path.join(BASE_DIR, "Database", "smartproperty.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Toggle for later PostgreSQL migration:
# DATABASE_URL = "postgresql://user:pass@localhost:5432/smartproperty"

APP_NAME = "Smart Property Management System"
APP_VERSION = "0.1.0"