print(">>> report_controller.py V1 <<<")

from Services.report_service import ReportService


class ReportController:
    def __init__(self):
        self.service = ReportService()

    def generate_summary(self):        return self.service.generate_summary_report()
    def generate_property(self):       return self.service.generate_property_report()
    def generate_payment(self):        return self.service.generate_payment_report()
    def generate_lease(self):          return self.service.generate_lease_report()
    def generate_maintenance(self):    return self.service.generate_maintenance_report()