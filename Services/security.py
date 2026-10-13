
import bcrypt

_MAX_BYTES = 72


def hash_password(plain: str) -> str:
    if plain is None:
        plain = ""
    data = plain.encode("utf-8")[:_MAX_BYTES]
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        data = plain.encode("utf-8")[:_MAX_BYTES]
        return bcrypt.checkpw(data, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---- Security question answers -------------------------------------------
# We normalise the answer (trim + lowercase) before hashing so that
# "Cape Town", "cape town " and "CAPE TOWN" all verify correctly.

def normalise_answer(answer: str) -> str:
    return (answer or "").strip().lower()


def hash_answer(answer: str) -> str:
    return hash_password(normalise_answer(answer))


def verify_answer(answer: str, hashed: str) -> bool:
    return verify_password(normalise_answer(answer), hashed)
