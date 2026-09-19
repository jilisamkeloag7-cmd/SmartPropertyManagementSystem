print(">>> auth_service.py V2 <<<")

from Repositories.user_repository import UserRepository
from Services.security import hash_password, verify_password
from Models.user import User, UserRole


# Map the role string emitted by the User Type screen → UserRole enum
_ROLE_LOOKUP = {
    "Administrator":     UserRole.ADMIN,
    "Property Manager":  UserRole.MANAGER,
    "Owner":             UserRole.OWNER,
    "Tenant / User":     UserRole.TENANT,
    "Tenant":            UserRole.TENANT,
    "User":              UserRole.TENANT,
}


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    # ------------------------------------------------------------------ auth
    def authenticate(self, identifier: str, password: str,
                     expected_role: str | None = None):
        """
        Returns (success: bool, user_dict | None, error_message | None)
        """
        if not identifier or not password:
            return False, None, "Please enter both your ID/email and password."

        user = self.users.find_by_login(identifier.strip())

        # 1. User must exist FIRST — before we touch any attribute
        if user is None:
            return False, None, "No account found with those details."

        # 2. User must be active
        if user.status == "Inactive":
            return False, None, "This account has been deactivated."

        # 3. Password must match
        if not verify_password(password, user.password_hash):
            return False, None, "Incorrect password."

        # 4. Role gate (if a specific role was selected on the UI)
        if expected_role and expected_role in _ROLE_LOOKUP:
            if user.role != _ROLE_LOOKUP[expected_role]:
                return (False, None,
                        f"This account is not registered as {expected_role}.")

        user_dict = {
            "user_id":   user.user_id,
            "id_number": user.id_number,
            "name":      user.name,
            "email":     user.email,
            "phone":     user.phone,
            "role":      user.role.value,
        }
        return True, user_dict, None

    # ------------------------------------------------------------------ register
    def register(self, id_number, name, email, phone, password, role: UserRole):
        """Create a new user with a hashed password."""
        if self.users.find_by_email(email):
            return False, "An account with that email already exists."
        if self.users.find_by_id_number(id_number):
            return False, "An account with that ID number already exists."

        user = User(
            id_number=id_number, name=name, email=email, phone=phone,
            password_hash=hash_password(password), role=role, status="Active"
        )
        self.users.create(user)
        return True, "Account created successfully."