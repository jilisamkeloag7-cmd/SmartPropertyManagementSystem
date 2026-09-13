"""Data-access layer for User entities."""
from Database.connection import get_session
from Models.user import User, UserRole

class UserRepository:
    def find_by_email(self, email: str) -> User | None:
        db = get_session()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()

    def find_by_id_number(self, id_number: str) -> User | None:
        db = get_session()
        try:
            return db.query(User).filter(User.id_number == id_number).first()
        finally:
            db.close()

    def find_by_login(self, identifier: str) -> User | None:
        """Look up by email OR ID number (login accepts either)."""
        db = get_session()
        try:
            return (
                db.query(User)
                .filter((User.email == identifier) | (User.id_number == identifier))
                .first()
            )
        finally:
            db.close()

    def create(self, user: User) -> User:
        db = get_session()
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def update_password(self, user_id: int, new_hash: str) -> bool:
        db = get_session()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            user.password_hash = new_hash
            db.commit()
            return True
        finally:
            db.close()