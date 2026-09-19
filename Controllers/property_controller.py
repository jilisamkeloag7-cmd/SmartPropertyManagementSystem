print(">>> property_controller.py V1 <<<")

from Services.property_service import PropertyService


class PropertyController:
    def __init__(self):
        self.service = PropertyService()

    def list(self, filters: dict | None = None):
        return self.service.list_properties(filters)

    def get(self, property_id: int):
        return self.service.get_property(property_id)

    def create(self, data: dict, session_user: dict):
        return self.service.create_property(data, session_user)

    def update(self, property_id: int, data: dict, session_user: dict):
        return self.service.update_property(property_id, data, session_user)

    def archive(self, property_id: int, session_user: dict):
        return self.service.archive_property(property_id, session_user)