print(">>> user_repository.py V3 <<<")

from sqlalchemy import func
from Database.connection import get_session
from Models.user import User, UserRole


class UserRepository:
    # ------------------------------------------------------------------ reads
    def find_by_email(self, email: str):
        """Case-insensitive email lookup."""
        if not email:
            return None
        db = get_session()
        try:
            return (
                db.query(User)
                .filter(func.lower(User.email) == email.strip().lower())
                .first()
            )
        finally:
            db.close()

    def find_by_id_number(self, id_number: str):
        db = get_session()
        try:
            return db.query(User).filter(User.id_number == id_number).first()
        finally:
            db.close()

    def find_by_id(self, user_id: int):
        db = get_session()
        try:
            return db.query(User).filter(User.user_id == user_id).first()
        finally:
            db.close()

    def find_by_login(self, identifier: str):
        """
        Login accepts email OR ID number.
        Email comparison is CASE-INSENSITIVE.
        ID number comparison is exact (digits only).
        """
        if not identifier:
            return None
        identifier = identifier.strip()
        db = get_session()
        try:
            return (
                db.query(User)
                .filter(
                    (func.lower(User.email) == identifier.lower())
                    | (User.id_number == identifier)
                )
                .first()
            )
        finally:
            db.close()

    def list_all(self):
        db = get_session()
        try:
            return db.query(User).order_by(User.user_id).all()
        finally:
            db.close()

    def search(self, query: str = "", role_filter: str | None = None,
               status_filter: str | None = None):
        db = get_session()
        try:
            q = db.query(User)
            if query:
                like = f"%{query}%"
                q = q.filter(
                    (User.name.ilike(like))
                    | (func.lower(User.email).like(f"%{query.lower()}%"))
                    | (User.id_number.ilike(like))
                )
            if role_filter and role_filter != "All":
                q = q.filter(User.role == UserRole(role_filter))
            if status_filter and status_filter != "All":
                q = q.filter(User.status == status_filter)
            return q.order_by(User.user_id).all()
        finally:
            db.close()

    # ------------------------------------------------------------------ writes
    def create(self, user: User) -> User:
        db = get_session()
        try:
            # Normalise email to lowercase on store so future lookups are simple
            user.email = (user.email or "").strip().lower()
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def update(self, user_id: int, name: str, email: str, phone: str,
               role: UserRole, status: str):
        db = get_session()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None
            user.name = name
            user.email = (email or "").strip().lower()
            user.phone = phone
            user.role = role
            user.status = status
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

    def deactivate(self, user_id: int) -> bool:
        db = get_session()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            user.status = "Inactive"
            db.commit()
            return True
        finally:
            db.close()

    def reactivate(self, user_id: int) -> bool:
        db = get_session()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            user.status = "Active"
            db.commit()
            return True
        finally:
            db.close()

    def has_active_links(self, user_id: int) -> bool:
        """True if the user has leases, ownerships or maintenance records."""
        from Models.lease import Lease
        from Models.ownership import Ownership
        from Models.maintenance import MaintenanceRequest
        db = get_session()
        try:
            if db.query(Lease).filter(Lease.tenant_id == user_id).count() > 0:
                return True
            if db.query(Ownership).filter(Ownership.user_id == user_id).count() > 0:
                return True
            if db.query(MaintenanceRequest).filter(
                MaintenanceRequest.submitted_by == user_id
            ).count() > 0:
                return True
            return False
        finally:
            db.close()

    def delete(self, user_id: int) -> bool:
        db = get_session()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True
        finally:
            db.close()