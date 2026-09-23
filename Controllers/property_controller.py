print(">>> property_controller.py V3 <<<")

from Services.property_service import PropertyService
from Services.property_image_service import PropertyImageService


class PropertyController:
    def __init__(self):
        self.service = PropertyService()
        self.images = PropertyImageService()

    # ---- properties
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

    # ---- owner flow
    def owner_submit(self, data: dict, session_user: dict):
        return self.service.owner_submit_property(data, session_user)

    def owner_update(self, property_id: int, data: dict, session_user: dict):
        return self.service.owner_update_property(property_id, data, session_user)

    def owner_withdraw(self, property_id: int, session_user: dict):
        return self.service.owner_withdraw_property(property_id, session_user)

    # ---- approval flow
    def approve(self, property_id: int, session_user: dict):
        return self.service.approve_property(property_id, session_user)

    def reject(self, property_id: int, reason: str, session_user: dict):
        return self.service.reject_property(property_id, reason, session_user)

    # ---- images
    def list_images(self, property_id: int):
        return self.images.list_for_property(property_id)

    def first_image_path(self, property_id: int):
        return self.images.first_image_path(property_id)

    def add_image(self, property_id: int, source_path: str, session_user: dict):
        return self.images.add_image(property_id, source_path, session_user)

    def remove_image(self, image_id: int, session_user: dict):
        return self.images.remove_image(image_id, session_user)