print(">>> ownership_controller.py V1 <<<")

from Services.ownership_service import OwnershipService


class OwnershipController:
    def __init__(self):
        self.service = OwnershipService()

    def list(self, filters: dict | None = None, session_user: dict | None = None):
        return self.service.list_ownerships(filters, session_user)

    def get(self, ownership_id: int):
        return self.service.get_ownership(ownership_id)

    def add(self, data: dict, session_user: dict):
        return self.service.add_ownership(data, session_user)

    def end(self, ownership_id: int, session_user: dict):
        return self.service.end_ownership(ownership_id, session_user)

    def share_total(self, property_id: int) -> float:
        return self.service.share_total(property_id)