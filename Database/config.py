
import os
import sys

# Load .env if present (used for cloud mode)
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    if os.path.isfile(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass


def _base_dir():
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        internal = os.path.join(exe_dir, "_internal")
        if os.path.isdir(internal):
            return internal
        return exe_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _base_dir()
DB_PATH = os.path.join(BASE_DIR, "Database", "smartproperty.db")

# Cloud PostgreSQL if DATABASE_URL is set, otherwise local SQLite
_cloud_url = os.environ.get("DATABASE_URL", "").strip()
IS_CLOUD = bool(_cloud_url and _cloud_url.startswith("postgresql"))

if IS_CLOUD:
    DATABASE_URL = _cloud_url
    print(f"[config] Cloud mode: PostgreSQL at {_cloud_url.split('@')[-1]}")
else:
    DATABASE_URL = os.environ.get("SPMS_DATABASE_URL", f"sqlite:///{DB_PATH}")
    print(f"[config] Local mode: SQLite at {DB_PATH}")

APP_NAME = "Smart Property Management System"
APP_VERSION = "1.0.0"

# Supabase Storage
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "property-images")
SUPABASE_PROFILE_BUCKET = os.environ.get("SUPABASE_PROFILE_BUCKET", "profile-images")
USE_CLOUD_STORAGE = bool(SUPABASE_URL and SUPABASE_ANON_KEY)
