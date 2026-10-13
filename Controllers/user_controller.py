
from Services.user_service import UserService


class UserController:
    def __init__(self):
        self.service = UserService()

    def list(self, filters: dict | None = None):
        return self.service.list_users(filters)

    def get(self, user_id: int):
        return self.service.get_user(user_id)

    def create(self, data: dict, session_user: dict):
        return self.service.create_user(data, session_user)

    def update(self, user_id: int, data: dict, session_user: dict):
        return self.service.update_user(user_id, data, session_user)

    def deactivate(self, user_id: int, session_user: dict):
        return self.service.deactivate_user(user_id, session_user)

    def reactivate(self, user_id: int, session_user: dict):
        return self.service.reactivate_user(user_id, session_user)

    def delete(self, user_id: int, session_user: dict):
        return self.service.delete_user(user_id, session_user)
    
