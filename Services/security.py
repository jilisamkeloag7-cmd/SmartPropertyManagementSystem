"""Password hashing and verification using bcrypt."""
import bcrypt

# bcrypt truncates at 72 bytes; enforce a sane limit
_MAX_BYTES = 72

def hash_password(plain: str) -> str:
    """Return a bcrypt hash (UTF-8 string) for the given password."""
    if plain is None:
        plain = ""
    data = plain.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    """Safely compare a plain password against a bcrypt hash."""
    if not plain or not hashed:
        return False
    try:
        data = plain.encode("utf-8")[:_MAX_BYTES]
        return bcrypt.checkpw(data, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False