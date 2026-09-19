print(">>> user_service.py V1 <<<")

from Repositories.user_repository import UserRepository
from Services.security import hash_password
from Models.user import User, UserRole

VALID_ROLES = {r.value for r in UserRole}
VALID_STATUSES = {"Active", "Inactive"}


class UserService:
    def __init__(self):
        self.users = UserRepository()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_admin(session_user):
        if not session_user or session_user.get("role") != UserRole.ADMIN.value:
            return False, "Access denied: administrators only."
        return True, None

    @staticmethod
    def _to_dict(u):
        return {
            "user_id": u.user_id,
            "id_number": u.id_number,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role.value if u.role else "",
            "status": u.status,
            "created_at": u.created_at,
        }

    # ------------------------------------------------------------------ reads
    def list_users(self, filters: dict | None = None):
        filters = filters or {}
        rows = self.users.search(
            query=filters.get("query", ""),
            role_filter=filters.get("role", "All"),
            status_filter=filters.get("status", "All"),
        )
        return [self._to_dict(u) for u in rows]

    def get_user(self, user_id: int):
        u = self.users.find_by_id(user_id)
        return self._to_dict(u) if u else None

    # ------------------------------------------------------------------ writes
    def create_user(self, data: dict, session_user: dict):
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err

        # ---- validate
        name = (data.get("name") or "").strip()
        id_number = (data.get("id_number") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        password = data.get("password") or ""
        role_str = data.get("role")
        status = data.get("status", "Active")

        if not name:
            return False, "Name is required."
        if not id_number:
            return False, "ID number is required."
        if not email:
            return False, "Email is required."
        if "@" not in email:
            return False, "Email format is invalid."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if role_str not in VALID_ROLES:
            return False, f"Role must be one of: {', '.join(sorted(VALID_ROLES))}."
        if status not in VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."

        if self.users.find_by_email(email):
            return False, "An account with that email already exists."
        if self.users.find_by_id_number(id_number):
            return False, "An account with that ID number already exists."

        user = User(
            id_number=id_number,
            name=name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role=UserRole(role_str),
            status=status,
        )
        created = self.users.create(user)
        return True, f"User #{created.user_id} created."

    def update_user(self, user_id: int, data: dict, session_user: dict):
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        role_str = data.get("role")
        status = data.get("status", "Active")

        if not name:
            return False, "Name is required."
        if not email or "@" not in email:
            return False, "A valid email is required."
        if role_str not in VALID_ROLES:
            return False, f"Role must be one of: {', '.join(sorted(VALID_ROLES))}."
        if status not in VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."

        # email uniqueness (excluding self)
        existing = self.users.find_by_email(email)
        if existing and existing.user_id != user_id:
            return False, "Another account already uses that email."

        updated = self.users.update(
            user_id=user_id, name=name, email=email, phone=phone,
            role=UserRole(role_str), status=status,
        )
        if not updated:
            return False, "User not found."
        return True, "User updated."

    def deactivate_user(self, user_id: int, session_user: dict):
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err
        # Prevent admin from deactivating themselves
        if session_user.get("user_id") == user_id:
            return False, "You cannot deactivate your own account."
        ok = self.users.deactivate(user_id)
        return (True, "User deactivated.") if ok else (False, "User not found.")

    def reactivate_user(self, user_id: int, session_user: dict):
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err
        ok = self.users.reactivate(user_id)
        return (True, "User reactivated.") if ok else (False, "User not found.")

    def delete_user(self, user_id: int, session_user: dict):
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err
        if session_user.get("user_id") == user_id:
            return False, "You cannot delete your own account."
        if self.users.has_active_links(user_id):
            return False, "Cannot delete: user has linked leases, ownerships or maintenance records. Deactivate instead."
        ok = self.users.delete(user_id)
        return (True, "User deleted.") if ok else (False, "User not found.")