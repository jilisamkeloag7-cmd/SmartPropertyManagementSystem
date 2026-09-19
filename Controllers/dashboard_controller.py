print(">>> dashboard_controller.py V1 <<<")

from Services.dashboard_service import DashboardService


class DashboardController:
    def __init__(self):
        self.service = DashboardService()

    def aggregate_for(self, user: dict):
        return self.service.aggregate_for(user)