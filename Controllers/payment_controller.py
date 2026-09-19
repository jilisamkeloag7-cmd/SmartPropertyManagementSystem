print(">>> payment_controller.py V1 <<<")

from Services.payment_service import PaymentService


class PaymentController:
    def __init__(self):
        self.service = PaymentService()

    def list(self, filters: dict | None = None):
        return self.service.list_payments(filters)

    def get(self, payment_id: int):
        return self.service.get_payment(payment_id)

    def create(self, data: dict, session_user: dict):
        return self.service.create_payment(data, session_user)

    def mark_paid(self, payment_id: int, paid_date, session_user: dict):
        return self.service.mark_paid(payment_id, paid_date, session_user)

    def check_overdue(self) -> int:
        return self.service.check_overdue()