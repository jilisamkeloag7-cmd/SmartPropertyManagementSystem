
import socket
from Database.config import IS_CLOUD, DATABASE_URL


def _parse_host_port():
    """Extract host and port from DATABASE_URL."""
    try:
        after_at = DATABASE_URL.split("@", 1)[1]
        host_port = after_at.split("/", 1)[0]
        parts = host_port.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 5432
        return host, port
    except Exception:
        return None, None


def is_online(timeout: float = 3.0) -> bool:
    """
    Return True if we can reach the cloud database host.
    In local (SQLite) mode, always returns True.
    """
    if not IS_CLOUD:
        return True

    host, port = _parse_host_port()
    if not host:
        return True  # can't parse — assume ok, let the DB layer decide

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error, OSError):
        return False
