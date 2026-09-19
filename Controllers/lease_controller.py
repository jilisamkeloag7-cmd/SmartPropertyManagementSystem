print(">>> lease_controller.py V1 <<<")

from Services.lease_service import LeaseService


class LeaseController:
    def __init__(self):
        self.service = LeaseService()

    def list(self, filters: dict | None = None):
        return self.service.list_leases(filters)

    def get(self, lease_id: int):
        return self.service.get_lease(lease_id)

    def create(self, data: dict, session_user: dict):
        return self.service.create_lease(data, session_user)

    def terminate(self, lease_id: int, session_user: dict):
        return self.service.terminate_lease(lease_id, session_user)

    def check_expiring(self, threshold_days: int = 30):
        return self.service.check_expiring(threshold_days)