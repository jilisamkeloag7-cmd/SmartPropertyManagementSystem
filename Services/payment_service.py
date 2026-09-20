print(">>> payment_service.py V2 <<<")

from datetime import date
from Repositories.payment_repository import PaymentRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService


WRITE_ROLES = {"Administrator", "Property Manager"}


class PaymentService:
    def __init__(self):
        self.payments = PaymentRepository()
        self.leases = LeaseRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()
        self.notifications = NotificationService()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to modify payments."
        return True, None

    @staticmethod
    def _to_dict(payment, lease=None, prop=None, tenant=None):
        return {
            "payment_id": payment.payment_id,
            "lease_id": payment.lease_id,
            "amount": payment.amount,
            "due_date": payment.due_date,
            "paid_date": payment.paid_date,
            "status": payment.status,
            "property_id": lease.property_id if lease else None,
            "property_address": prop.address if prop else "",
            "tenant_id": lease.tenant_id if lease else None,
            "tenant_name": tenant.name if tenant else "",
            "tenant_email": tenant.email if tenant else "",
        }

    def _enrich(self, payment):
        lease = self.leases.find_by_id(payment.lease_id)
        prop = self.properties.find_by_id(lease.property_id) if lease else None
        tenant = self.users.find_by_id(lease.tenant_id) if lease else None
        return self._to_dict(payment, lease, prop, tenant)

    # ------------------------------------------------------------------ reads
    def list_payments(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        rows = self.payments.list_all()

        # -------- role-based visibility filter
        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Tenant" and uid:
            allowed_lease_ids = {l.lease_id for l in self.leases.list_for_tenant(uid)}
            rows = [p for p in rows if p.lease_id in allowed_lease_ids]
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            allowed_lease_ids = set()
            for p in rows:
                lease = self.leases.find_by_id(p.lease_id)
                if lease and lease.property_id in owned_pids:
                    allowed_lease_ids.add(p.lease_id)
            rows = [p for p in rows if p.lease_id in allowed_lease_ids]
        # Admin/Manager: no additional filtering

        # -------- user-driven filters
        out = []
        for p in rows:
            d = self._enrich(p)
            if status_filter and status_filter != "All" and d["status"] != status_filter:
                continue
            if query:
                haystack = f"{d['property_address']} {d['tenant_name']} {d['tenant_email']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_payment(self, payment_id: int):
        p = self.payments.find_by_id(payment_id)
        return self._enrich(p) if p else None

    # ------------------------------------------------------------------ writes
    def create_payment(self, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        try:
            lease_id = int(data.get("lease_id") or 0)
            amount = float(data.get("amount") or 0)
        except (TypeError, ValueError):
            return False, "Invalid numeric value."

        due_date = data.get("due_date")

        if amount <= 0:
            return False, "Amount must be greater than zero."
        if not due_date:
            return False, "Due date is required."

        lease = self.leases.find_by_id(lease_id)
        if not lease:
            return False, "Lease not found."

        p = self.payments.create(
            lease_id=lease_id,
            amount=amount,
            due_date=due_date,
            status="Pending",
        )
        return True, f"Payment #{p.payment_id} created."

    def mark_paid(self, payment_id: int, paid_date, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        payment = self.payments.find_by_id(payment_id)
        if not payment:
            return False, "Payment not found."
        if payment.status == "Paid":
            return False, "Payment is already marked as Paid."

        if paid_date is None:
            paid_date = date.today()

        self.payments.mark_paid(payment_id, paid_date)
        return True, f"Payment #{payment_id} marked as Paid."

    def check_overdue(self) -> int:
        today = date.today()
        newly_overdue = 0

        for payment in self.payments.find_pending():
            if payment.due_date and payment.due_date < today:
                self.payments.set_status(payment.payment_id, "Overdue")

                lease = self.leases.find_by_id(payment.lease_id)
                if lease:
                    self.notifications.emit(
                        user_id=lease.tenant_id,
                        type="payment_overdue",
                        title="Payment overdue",
                        message=(
                            f"Payment #{payment.payment_id} of "
                            f"R{payment.amount:.2f} was due on {payment.due_date}."
                        ),
                        priority="High",
                    )
                newly_overdue += 1

        return newly_overdue