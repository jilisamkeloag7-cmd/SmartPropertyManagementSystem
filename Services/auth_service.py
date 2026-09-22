print(">>> auth_service.py V3 <<<")

from Repositories.user_repository import UserRepository
from Services.security import (hash_password, verify_password,
                                hash_answer, verify_answer)
from Models.user import User, UserRole


_ROLE_LOOKUP = {
    "Administrator":     UserRole.ADMIN,
    "Property Manager":  UserRole.MANAGER,
    "Owner":             UserRole.OWNER,
    "Tenant / User":     UserRole.TENANT,
    "Tenant":            UserRole.TENANT,
    "User":              UserRole.TENANT,
}

# Roles a user can self-register for via the public registration form
SELF_REGISTER_ROLES = {
    "Tenant": UserRole.TENANT,
    "Owner":  UserRole.OWNER,
}


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    # ------------------------------------------------------------------ login
    def authenticate(self, identifier: str, password: str,
                     expected_role: str | None = None):
        if not identifier or not password:
            return False, None, "Please enter both your ID/email and password."

        user = self.users.find_by_login(identifier.strip())

        if user is None:
            return False, None, "No account found with those details."

        if user.status == "Inactive":
            return False, None, "This account has been deactivated."

        if user.status == "Pending Approval":
            return False, None, "This account is awaiting administrator approval."

        if not verify_password(password, user.password_hash):
            return False, None, "Incorrect password."

        if expected_role and expected_role in _ROLE_LOOKUP:
            if user.role != _ROLE_LOOKUP[expected_role]:
                return False, None, f"This account is not registered as {expected_role}."

        user_dict = {
            "user_id":   user.user_id,
            "id_number": user.id_number,
            "name":      user.name,
            "email":     user.email,
            "phone":     user.phone,
            "role":      user.role.value,
        }
        return True, user_dict, None

    # ------------------------------------------------------------------ register (admin-only, legacy)
    def register(self, id_number, name, email, phone, password, role: UserRole):
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

    # ------------------------------------------------------------------ self-registration
    def register_self(self, id_number, name, email, phone, password,
                      role_str, security_question, security_answer):
        """
        Public self-registration for Tenant and Owner.
        Creates an Active account and stores the security question for recovery.
        """
        # ---- Validate
        name = (name or "").strip()
        id_number = (id_number or "").strip()
        email = (email or "").strip().lower()
        phone = (phone or "").strip()
        password = password or ""

        if not name:
            return False, "Full name is required."
        if not id_number:
            return False, "ID number is required."
        if not email or "@" not in email:
            return False, "A valid email is required."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if role_str not in SELF_REGISTER_ROLES:
            return False, "You can only register as a Tenant or Owner."

        if not security_question:
            return False, "Please choose a security question."
        if len((security_answer or "").strip()) < 3:
            return False, "Security answer must be at least 3 characters."

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
            role=SELF_REGISTER_ROLES[role_str],
            status="Active",
            security_question=security_question,
            security_answer_hash=hash_answer(security_answer),
        )
        created = self.users.create(user)
        return True, f"Account created. Welcome, {created.name}!"

    # ------------------------------------------------------------------ forgot password
    def get_security_question(self, email: str):
        """Step 1 of recovery: return the question (or None)."""
        if not email:
            return None
        user = self.users.find_by_email(email.strip())
        if not user or not user.security_question:
            return None
        return user.security_question

    def verify_security_answer(self, email: str, answer: str):
        """Step 2 of recovery: verify the answer."""
        user = self.users.find_by_email(email.strip())
        if not user or not user.security_answer_hash:
            return False, "This account has no security question configured."
        if not verify_answer(answer, user.security_answer_hash):
            return False, "Incorrect answer. Please try again."
        return True, "Verified."

    def reset_password(self, email: str, answer: str, new_password: str):
        """Step 3 of recovery: verify once more, then change password."""
        if len(new_password or "") < 6:
            return False, "New password must be at least 6 characters."

        user = self.users.find_by_email(email.strip())
        if not user:
            return False, "Account not found."
        if not verify_answer(answer, user.security_answer_hash):
            return False, "Security answer verification failed."

        self.users.update_password(user.user_id, hash_password(new_password))
        return True, "Password reset. You can now sign in."