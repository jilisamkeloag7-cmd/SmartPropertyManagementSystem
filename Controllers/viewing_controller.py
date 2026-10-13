
from Services.viewing_service import ViewingService


class ViewingController:
    def __init__(self):
        self.service = ViewingService()

    def list(self, filters: dict | None = None, session_user: dict | None = None):
        return self.service.list_requests(filters, session_user)

    def get(self, request_id: int):
        return self.service.get_request(request_id)

    def pending_count(self) -> int:
        return self.service.pending_count()

    def request(self, property_id, preferred_date, preferred_time, message, session_user):
        return self.service.request_viewing(property_id, preferred_date,
                                            preferred_time, message, session_user)

    def approve(self, request_id: int, manager_note: str, session_user: dict):
        return self.service.approve(request_id, manager_note, session_user)

    def decline(self, request_id: int, reason: str, session_user: dict):
        return self.service.decline(request_id, reason, session_user)

    def cancel(self, request_id: int, session_user: dict):
        return self.service.cancel(request_id, session_user)
