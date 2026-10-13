
from Services.report_service import ReportService


class ReportController:
    def __init__(self):
        self.service = ReportService()

    # ---- admin / manager
    def generate_summary(self):
        return self.service.generate_summary_report()

    def generate_property(self):
        return self.service.generate_property_report()

    def generate_payment(self):
        return self.service.generate_payment_report()

    def generate_lease(self):
        return self.service.generate_lease_report()

    def generate_maintenance(self):
        return self.service.generate_maintenance_report()

    # ---- owner
    def generate_owner_summary(self, session_user: dict):
        return self.service.generate_owner_summary(session_user)

    def generate_owner_income(self, session_user: dict, months_back: int = 12):
        return self.service.generate_owner_income(session_user, months_back)

    def generate_owner_tenants(self, session_user: dict):
        return self.service.generate_owner_tenants(session_user)
