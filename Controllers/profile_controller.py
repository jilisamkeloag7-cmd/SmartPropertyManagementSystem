print(">>> profile_controller.py V1 <<<")

from Services.profile_service import ProfileService


class ProfileController:
    def __init__(self):
        self.service = ProfileService()

    # ---- reads
    def get(self, user_id: int):
        return self.service.get_profile(user_id)

    def list_pending_requests(self):
        return self.service.list_pending_requests()

    def list_all_requests(self):
        return self.service.list_all_requests()

    def list_my_requests(self, user_id: int):
        return self.service.list_my_requests(user_id)

    def pending_count(self) -> int:
        return self.service.pending_count()

    # ---- direct edits
    def update_phone(self, user_id: int, phone: str):
        return self.service.update_phone(user_id, phone)

    def update_security_qa(self, user_id: int, question: str, answer: str):
        return self.service.update_security_qa(user_id, question, answer)

    def change_password(self, user_id, old, new, confirm):
        return self.service.change_password(user_id, old, new, confirm)

    def upload_image(self, user_id: int, source_path: str):
        return self.service.upload_profile_image(user_id, source_path)

    def remove_image(self, user_id: int):
        return self.service.remove_profile_image(user_id)

    # ---- change requests
    def request_change(self, user_id, field, new_value, reason):
        return self.service.request_change(user_id, field, new_value, reason)

    def cancel_request(self, request_id: int, session_user: dict):
        return self.service.cancel_request(request_id, session_user)

    def approve_change(self, request_id: int, session_user: dict):
        return self.service.approve_change(request_id, session_user)

    def reject_change(self, request_id: int, reason: str, session_user: dict):
        return self.service.reject_change(request_id, reason, session_user)