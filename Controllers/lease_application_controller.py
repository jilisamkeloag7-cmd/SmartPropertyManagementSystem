print(">>> lease_application_controller.py V1 <<<")

from Services.lease_application_service import LeaseApplicationService


class LeaseApplicationController:
    def __init__(self):
        self.service = LeaseApplicationService()

    def list(self, filters: dict | None = None, session_user: dict | None = None):
        return self.service.list_applications(filters, session_user)

    def get(self, application_id: int):
        return self.service.get_application(application_id)

    def apply(self, property_id, preferred_start, duration_months, message, session_user):
        return self.service.apply(property_id, preferred_start,
                                   duration_months, message, session_user)

    def approve(self, application_id: int, note: str, session_user: dict):
        return self.service.approve(application_id, note, session_user)

    def decline(self, application_id: int, reason: str, session_user: dict):
        return self.service.decline(application_id, reason, session_user)

    def withdraw(self, application_id: int, session_user: dict):
        return self.service.withdraw(application_id, session_user)