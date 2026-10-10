print(">>> payment_service.py V5 <<<")

from datetime import date, datetime
from Repositories.payment_repository import PaymentRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService


WRITE_ROLES   = {"Administrator", "Property Manager"}
CONFIRM_ROLES = {"Administrator", "Property Manager"}
ADMIN_ONLY    = {"Administrator"}

# Roles that should receive broadcast notifications for payment events
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

    def _enrich(self, payment):
        lease = self.leases.find_by_id(payment.lease_id)
        prop = self.properties.find_by_id(lease.property_id) if lease else None
        tenant = self.users.find_by_id(lease.tenant_id) if lease else None
        return self._to_dict(payment, lease, prop, tenant)

    # ------------------------------------------------------------------ broadcast helper
    def _broadcast_payment_event(self, payment, event_type, title, message,
                                  priority="Normal", exclude_user_id=None):
        """
        Send a notification to every party related to a payment:
        - The tenant on the lease
        - The property owner(s)
        - Every administrator
        - Every property manager

        Duplicate user_ids are de-duplicated so no one gets the notification twice.
        """
        notified = set()

        lease = self.leases.find_by_id(payment.lease_id)
        if not lease:
            print(f"[payment-broadcast] Lease #{payment.lease_id} not found — aborting")
            return

        # 1. Tenant
        if lease.tenant_id and lease.tenant_id != exclude_user_id:
            self.notifications.emit(
                user_id=lease.tenant_id,
                type=event_type,
                title=title,
                message=message,
                priority=priority,
            )
            notified.add(lease.tenant_id)

        # 2. Property owner(s)
        for o in self.ownerships.list_for_property(lease.property_id):
            if o.user_id in notified or o.user_id == exclude_user_id:
                continue
            self.notifications.emit(
                user_id=o.user_id,
                type=event_type,
                title=title,
                message=message,
                priority=priority,
            )
            notified.add(o.user_id)

        # 3. Administrators + Property Managers
        for u in self.users.list_all():
            if u.role.value not in BROADCAST_ROLES:
                continue
            if u.user_id in notified or u.user_id == exclude_user_id:
                continue
            self.notifications.emit(
                user_id=u.user_id,
                type=event_type,
                title=title,
                message=message,
                priority=priority,
            )
            notified.add(u.user_id)

        print(f"[payment-broadcast] '{title}' sent to {len(notified)} user(s)")

    # ------------------------------------------------------------------ reads
    def list_payments(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        rows = self.payments.list_all()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Tenant" and uid:
            allowed = {l.lease_id for l in self.leases.list_for_tenant(uid)}
            rows = [p for p in rows if p.lease_id in allowed]
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            allowed = set()
            for p in rows:
                lease = self.leases.find_by_id(p.lease_id)
                if lease and lease.property_id in owned_pids:
                    allowed.add(p.lease_id)
            rows = [p for p in rows if p.lease_id in allowed]

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

    # ------------------------------------------------------------------ manager writes
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
        """
        Direct mark-paid — ADMIN ONLY.
        Broadcasts to every party related to the payment.
        """
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
            message=(
                f"Payment #{payment_id} of R{payment.amount:,.2f} has been "
                f"marked as Paid by an administrator."
            ),
            priority="Normal",
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
                    message=(
                        f"Payment #{payment.payment_id} of "
                        f"R{payment.amount:,.2f} was due on {payment.due_date}."
                    ),
                    priority="High",
                )
                newly_overdue += 1

        return newly_overdue

    # ------------------------------------------------------------------ tenant self-service
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
            return False, "You have already marked this payment. Awaiting manager confirmation."

        reference = (reference or "").strip()
        if len(reference) < 3:
            return False, "Please provide a payment reference or note (at least 3 characters)."

        self.payments.set_tenant_claim(payment_id, reference)

        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_awaiting_confirmation",
            title=f"Payment #{payment_id} awaiting confirmation",
            message=(
                f"{session_user.get('name', 'Tenant')} has marked "
                f"payment #{payment_id} (R{payment.amount:,.2f}) as paid. "
                f"Reference: {reference[:120]}"
            ),
            priority="High",
        )

        return True, "Payment marked. Awaiting manager confirmation."

    def manager_confirm(self, payment_id: int, session_user: dict):
        """Confirm a tenant-submitted payment claim. Broadcasts to all parties."""
        ok, err = self._assert_confirm_permission(session_user)
        if not ok:
            return False, err

        payment = self.payments.find_by_id(payment_id)
        if not payment:
            return False, "Payment not found."
        if payment.status != "Awaiting Confirmation":
            return False, f"Payment status is '{payment.status}' — nothing to confirm."

        self.payments.mark_paid(payment_id, date.today())

        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_confirmed",
            title=f"Payment #{payment_id} confirmed",
            message=(
                f"Payment #{payment_id} of R{payment.amount:,.2f} has been "
                f"confirmed as paid by {session_user.get('name', 'management')}."
            ),
            priority="Normal",
        )

        return True, f"Payment #{payment_id} confirmed as paid."

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
            return False, "Please provide a reason (at least 3 characters)."

        self.payments.clear_tenant_claim(payment_id, new_status="Pending")

        self._broadcast_payment_event(
            payment=payment,
            event_type="payment_rejected",
            title=f"Payment #{payment_id} claim rejected",
            message=(
                f"Payment claim for #{payment_id} was not confirmed. "
                f"Reason: {reason[:150]}"
            ),
            priority="High",
        )

        return True, "Payment claim rejected."