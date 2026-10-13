
from Services.payment_service import PaymentService


class PaymentController:
    def __init__(self):
        self.service = PaymentService()

    def list(self, filters: dict | None = None, session_user: dict | None = None):
        return self.service.list_payments(filters, session_user)

    def get(self, payment_id: int):
        return self.service.get_payment(payment_id)

    def create(self, data: dict, session_user: dict):
        return self.service.create_payment(data, session_user)

    def mark_paid(self, payment_id: int, paid_date, session_user: dict):
        return self.service.mark_paid(payment_id, paid_date, session_user)

    def check_overdue(self) -> int:
        return self.service.check_overdue()

    # ---- B6: tenant + manager flow
    def tenant_mark_paid(self, payment_id: int, reference: str, session_user: dict):
        return self.service.tenant_mark_paid(payment_id, reference, session_user)

    def manager_confirm(self, payment_id: int, session_user: dict):
        return self.service.manager_confirm(payment_id, session_user)

    def manager_reject(self, payment_id: int, reason: str, session_user: dict):
        return self.service.manager_reject(payment_id, reason, session_user)
