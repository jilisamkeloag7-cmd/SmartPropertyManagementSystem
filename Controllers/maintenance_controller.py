
from Services.maintenance_service import MaintenanceService


class MaintenanceController:
    def __init__(self):
        self.service = MaintenanceService()

    def list(self, filters: dict | None = None, session_user: dict | None = None):
        return self.service.list_requests(filters, session_user)

    def get(self, request_id: int):
        return self.service.get_request(request_id)

    def submit(self, data: dict, session_user: dict):
        return self.service.submit_request(data, session_user)

    def update_status(self, request_id: int, new_status: str, session_user: dict):
        return self.service.update_status(request_id, new_status, session_user)
