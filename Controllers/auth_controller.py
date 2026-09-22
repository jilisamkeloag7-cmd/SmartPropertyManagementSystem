print(">>> auth_controller.py V3 <<<")

from Services.auth_service import AuthService


class AuthController:
    def __init__(self):
        self.service = AuthService()

    def login(self, identifier: str, password: str, selected_role: str | None = None):
        return self.service.authenticate(identifier, password, selected_role)

    def register_self(self, id_number, name, email, phone, password,
                      role_str, security_question, security_answer):
        return self.service.register_self(
            id_number, name, email, phone, password,
            role_str, security_question, security_answer,
        )

    def get_security_question(self, email: str):
        return self.service.get_security_question(email)

    def verify_security_answer(self, email: str, answer: str):
        return self.service.verify_security_answer(email, answer)

    def reset_password(self, email: str, answer: str, new_password: str):
        return self.service.reset_password(email, answer, new_password)