"""Controller — bridges UI events to AuthService."""
from Services.auth_service import AuthService


class AuthController:
    def __init__(self):
        self.service = AuthService()

    def login(self, identifier: str, password: str, selected_role: str | None = None):
        """Return (success, user_dict | None, error | None)."""
        return self.service.authenticate(identifier, password, selected_role)