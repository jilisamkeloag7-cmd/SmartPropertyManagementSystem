
from datetime import date, datetime
from Repositories.payment_repository import PaymentRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService
from Database.connection import get_session
from Models.lease import Lease
from Models.property import Property
from Models.user import User


WRITE_ROLES   = {"Administrator", "Property Manager"}
CONFIRM_ROLES = {"Administrator", "Property Manager"}
ADMIN_ONLY    = {"Administrator"}
BROADCAST_ROLES = {"Administrator", "Property Manager"}


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
    def _assert_confirm_permission(session_user):
        if not session_user or session_user.get("role") not in CONFIRM_ROLES:
            return False, "Only managers or administrators can confirm payments."
        return True, None

    @staticmethod
    def _assert_admin(session_user):
        if not session_user or session_user.get("role") not in ADMIN_ONLY:
            return False, "Only administrators can use the direct mark-paid action."
        return True, None

    # ------------------------------------------------------------------ batch prefetch
    @staticmethod
    def _prefetch_lookups():
        """Fetch all leases, properties and users in 3 queries total."""
        db = get_session()
        try:
            leases = {l.lease_id: l for l in db.query(Lease).all()}
            props = {p.property_id: p for p in db.query(Property).all()}
            users = {u.user_id: u for u in db.query(User).all()}
            return leases, props, users
        finally:
            db.close()

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
            "tenant_marked_at": payment.tenant_marked_at,
            "payment_reference": payment.payment_reference or "",
        }

    def _enrich(self, payment, leases_by_id, props_by_id, users_by_id):
        lease = leases_by_id.get(payment.lease_id)
        prop = props_by_id.get(lease.property_id) if lease else None
        tenant = users_by_id.get(lease.tenant_id) if lease else None
        return self._to_dict(payment, lease, prop, tenant)

    def _enrich_one(self, payment):
        """Single-item enrich for non-list operations (still 3 queries, fine)."""
        lease = self.leases.find_by_id(payment.lease_id)
        prop = self.properties.find_by_id(lease.property_id) if lease else None
        tenant = self.users.find_by_id(lease.tenant_id) if lease else None
        return self._to_dict(payment, lease, prop, tenant)

    # ------------------------------------------------------------------ broadcast helper
    def _broadcast_payment_event(self, payment, event_type, title, message,
                                  priority="Normal", exclude_user_id=None):
        notified = set()
        lease = self.leases.find_by_id(payment.lease_id)
        if not lease:
            return

        if lease.tenant_id and lease.tenant_id != exclude_user_id:
            self.notifications.emit(lease.tenant_id, event_type, title,
                                     message, priority)
            notified.add(lease.tenant_id)

        for o in self.ownerships.list_for_property(lease.property_id):
            if o.user_id in notified or o.user_id == exclude_user_id:
                continue
            self.notifications.emit(o.user_id, event_type, title,
                                     message, priority)
            notified.add(o.user_id)

        for u in self.users.list_all():
            if u.role.value not in BROADCAST_ROLES:
                continue
            if u.user_id in notified or u.user_id == exclude_user_id:
                continue
            self.notifications.emit(u.user_id, event_type, title,
                                     message, priority)
            notified.add(u.user_id)

    # ------------------------------------------------------------------ reads
    def list_payments(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        rows = self.payments.list_all()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        # ---- prefetch once
        leases_by_id, props_by_id, users_by_id = self._prefetch_lookups()

        # ---- role scoping
        if role == "Tenant" and uid:
            allowed = {l.lease_id for l in leases_by_id.values()
                       if l.tenant_id == uid}
            rows = [p for p in rows if p.lease_id in allowed]
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            allowed = {l.lease_id for l in leases_by_id.values()
                       if l.property_id in owned_pids}
            rows = [p for p in rows if p.lease_id in allowed]

        # ---- filter + enrich (all in memory now)
        out = []
        for p in rows:
            d = self._enrich(p, leases_by_id, props_by_id, users_by_id)
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
        return self._enrich_one(p) if p else None

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

        p = self.payments.create(lease_id, amount, due_date, status="Pending")
        return True, f"Payment #{p.payment_id} created."

    def mark_paid(self, payment_id: int, paid_date, session_user: dict):
        ok, err = self._assert_admin(session_user)
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
        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_paid",
            title=f"Payment #{payment_id} marked as Paid",
            message=f"Payment #{payment_id} of R{payment.amount:,.2f} marked as Paid.",
        )
        return True, f"Payment #{payment_id} marked as Paid."

    def check_overdue(self) -> int:
        today = date.today()
        newly_overdue = 0

        for payment in self.payments.find_pending():
            if payment.due_date and payment.due_date < today:
                self.payments.set_status(payment.payment_id, "Overdue")
                self._broadcast_payment_event(
                    payment=payment,
                    event_type="payment_overdue",
                    title=f"Payment #{payment.payment_id} overdue",
                    message=f"Payment #{payment.payment_id} of R{payment.amount:,.2f} "
                            f"was due on {payment.due_date}.",
                    priority="High",
                )
                newly_overdue += 1
        return newly_overdue

    def tenant_mark_paid(self, payment_id: int, reference: str, session_user: dict):
        role = session_user.get("role", "")
        uid = session_user.get("user_id")
        if role != "Tenant":
            return False, "Only tenants can use this action."

        payment = self.payments.find_by_id(payment_id)
        if not payment:
            return False, "Payment not found."

        lease = self.leases.find_by_id(payment.lease_id)
        if not lease or lease.tenant_id != uid:
            return False, "This payment does not belong to you."

        if payment.status == "Paid":
            return False, "This payment has already been confirmed as paid."
        if payment.status == "Awaiting Confirmation":
            return False, "You have already marked this payment."

        reference = (reference or "").strip()
        if len(reference) < 3:
            return False, "Please provide a reference (at least 3 characters)."

        self.payments.set_tenant_claim(payment_id, reference)
        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_awaiting_confirmation",
            title=f"Payment #{payment_id} awaiting confirmation",
            message=f"{session_user.get('name', 'Tenant')} marked payment "
                    f"#{payment_id} (R{payment.amount:,.2f}) as paid. "
                    f"Reference: {reference[:120]}",
            priority="High",
        )
        return True, "Payment marked. Awaiting manager confirmation."

    def manager_confirm(self, payment_id: int, session_user: dict):
        ok, err = self._assert_confirm_permission(session_user)
        if not ok:
            return False, err

        payment = self.payments.find_by_id(payment_id)
        if not payment:
            return False, "Payment not found."
        if payment.status != "Awaiting Confirmation":
            return False, f"Payment status is '{payment.status}'."

        self.payments.mark_paid(payment_id, date.today())
        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_confirmed",
            title=f"Payment #{payment_id} confirmed",
            message=f"Payment #{payment_id} of R{payment.amount:,.2f} "
                    f"was confirmed by {session_user.get('name', 'management')}.",
        )
        return True, f"Payment #{payment_id} confirmed."

    def manager_reject(self, payment_id: int, reason: str, session_user: dict):
        ok, err = self._assert_confirm_permission(session_user)
        if not ok:
            return False, err

        payment = self.payments.find_by_id(payment_id)
        if not payment:
            return False, "Payment not found."
        if payment.status != "Awaiting Confirmation":
            return False, "This payment is not awaiting confirmation."

        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason."

        self.payments.clear_tenant_claim(payment_id, new_status="Pending")
        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_rejected",
            title=f"Payment #{payment_id} claim rejected",
            message=f"Payment claim for #{payment_id} was not confirmed. "
                    f"Reason: {reason[:150]}",
            priority="High",
        )
        return True, "Payment claim rejected."
