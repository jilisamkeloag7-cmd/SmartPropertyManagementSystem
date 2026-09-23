print(">>> lease_application_service.py V2 <<<")

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from Repositories.lease_application_repository import LeaseApplicationRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.lease_service import LeaseService
from Services.notification_service import NotificationService


MANAGER_ROLES = {"Administrator", "Property Manager"}

MIN_DURATION_MONTHS = 1
MAX_DURATION_MONTHS = 36
MAX_START_DAYS_AHEAD = 90


class LeaseApplicationService:
    def __init__(self):
        self.applications = LeaseApplicationRepository()
        self.leases = LeaseRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()
        self.lease_service = LeaseService()
        self.notifications = NotificationService()

    # ------------------------------------------------------------------ helpers
    def _enrich(self, a):
        prop = self.properties.find_by_id(a.property_id)
        tenant = self.users.find_by_id(a.tenant_id)
        return {
            "application_id": a.application_id,
            "property_id": a.property_id,
            "property_address": prop.address if prop else "",
            "property_listing_price": prop.listing_price if prop else None,
            "tenant_id": a.tenant_id,
            "tenant_name": tenant.name if tenant else "",
            "tenant_email": tenant.email if tenant else "",
            "preferred_start": a.preferred_start,
            "duration_months": a.duration_months,
            "message": a.message or "",
            "status": a.status,
            "decision_note": a.decision_note or "",
            "created_lease_id": a.created_lease_id,
            "created_at": a.created_at,
            "decided_at": a.decided_at,
        }

    @staticmethod
    def _compute_end_date(start: date, duration_months: int) -> date:
        return start + relativedelta(months=duration_months)

    # ------------------------------------------------------------------ reads
    def list_applications(self, filters: dict | None = None,
                          session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Tenant" and uid:
            rows = self.applications.list_for_tenant(uid)
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            rows = [a for a in self.applications.list_all()
                    if a.property_id in owned_pids]
        else:
            rows = self.applications.list_all()

        out = []
        for a in rows:
            d = self._enrich(a)
            if status_filter and status_filter != "All" and d["status"] != status_filter:
                continue
            if query:
                haystack = f"{d['property_address']} {d['tenant_name']} {d['tenant_email']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_application(self, application_id: int):
        a = self.applications.find_by_id(application_id)
        return self._enrich(a) if a else None

    # ------------------------------------------------------------------ tenant submit
    def apply(self, property_id: int, preferred_start: date,
              duration_months: int, message: str, session_user: dict):
        role = session_user.get("role", "")
        uid = session_user.get("user_id")

        if role != "Tenant":
            return False, "Only tenants can apply for leases."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        if prop.status != "Available":
            return False, f"This property is {prop.status.lower()} — no longer accepting applications."

        if not preferred_start:
            return False, "Preferred start date is required."

        today = date.today()
        if preferred_start < today:
            return False, "Preferred start date cannot be in the past."

        if preferred_start > today + timedelta(days=MAX_START_DAYS_AHEAD):
            return False, f"Start date cannot be more than {MAX_START_DAYS_AHEAD} days away."

        try:
            duration_months = int(duration_months)
        except (TypeError, ValueError):
            return False, "Duration must be a number."

        if duration_months < MIN_DURATION_MONTHS or duration_months > MAX_DURATION_MONTHS:
            return False, f"Duration must be between {MIN_DURATION_MONTHS} and {MAX_DURATION_MONTHS} months."

        if self.applications.has_pending_for_property(property_id, uid):
            return False, "You already have a pending application for this property."

        msg = (message or "").strip()
        if len(msg) > 1000:
            return False, "Message is too long (max 1000 characters)."

        app = self.applications.create(
            property_id=property_id,
            tenant_id=uid,
            preferred_start=preferred_start,
            duration_months=duration_months,
            message=msg or None,
        )

        for u in self.users.list_all():
            if u.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    user_id=u.user_id,
                    type="lease_application_new",
                    title=f"New lease application — Property #{property_id}",
                    message=(
                        f"{session_user.get('name', 'Tenant')} applied for "
                        f"{prop.address} starting {preferred_start.isoformat()} "
                        f"for {duration_months} month(s)."
                    ),
                    priority="High",
                )

        return True, "Application submitted. Management will review it shortly."

    # ------------------------------------------------------------------ manager decision
    def approve(self, application_id: int, note: str, session_user: dict):
        if (session_user or {}).get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can approve applications."

        a = self.applications.find_by_id(application_id)
        if not a:
            return False, "Application not found."
        if a.status != "Pending":
            return False, f"Application is already {a.status}."

        prop = self.properties.find_by_id(a.property_id)
        if not prop:
            return False, "Property not found."

        if prop.status != "Available":
            self.applications.set_status(
                application_id, "Declined",
                decision_note=f"Property is no longer available ({prop.status.lower()}).",
            )
            self.notifications.emit(
                user_id=a.tenant_id,
                type="lease_application_declined",
                title=f"Application declined — {prop.address}",
                message=f"The property is no longer available ({prop.status.lower()}).",
                priority="Normal",
            )
            return False, "Property is no longer available. Application has been declined."

        end_date = self._compute_end_date(a.preferred_start, a.duration_months)

        lease_data = {
            "property_id": a.property_id,
            "tenant_id": a.tenant_id,
            "start_date": a.preferred_start,
            "end_date": end_date,
            "rent_amount": prop.listing_price if prop.listing_price else 0.0,
        }

        if not lease_data["rent_amount"] or lease_data["rent_amount"] <= 0:
            return False, "Property has no listing price — set a price before approving."

        ok, msg = self.lease_service.create_lease(lease_data, session_user)
        if not ok:
            return False, f"Failed to create lease: {msg}"

        leases = self.leases.list_for_tenant(a.tenant_id)
        active = [l for l in leases
                  if l.property_id == a.property_id and l.status == "Active"]
        created_lease_id = active[0].lease_id if active else None

        decision = (note or "").strip() or "Approved by management."
        self.applications.set_status(
            application_id, "Approved",
            decision_note=decision,
            created_lease_id=created_lease_id,
        )

        self.notifications.emit(
            user_id=a.tenant_id,
            type="lease_application_approved",
            title=f"Application approved — {prop.address}",
            message=(
                f"Your lease application for {prop.address} has been approved. "
                f"Lease #{created_lease_id} starts on {a.preferred_start.isoformat()}."
                + (f" Note: {decision}" if note else "")
            ),
            priority="High",
        )

        other_pending = [
            o for o in self.applications.list_pending_for_property(a.property_id)
            if o.application_id != application_id
        ]
        for o in other_pending:
            self.applications.set_status(
                o.application_id, "Declined",
                decision_note="Property has been leased to another applicant.",
            )
            self.notifications.emit(
                user_id=o.tenant_id,
                type="lease_application_declined",
                title=f"Application declined — {prop.address}",
                message="The property has been leased to another applicant.",
                priority="Normal",
            )

        return True, f"Application approved. Lease #{created_lease_id} created."

    def decline(self, application_id: int, reason: str, session_user: dict):
        if (session_user or {}).get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can decline applications."

        a = self.applications.find_by_id(application_id)
        if not a:
            return False, "Application not found."
        if a.status != "Pending":
            return False, f"Application is already {a.status}."

        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason (at least 3 characters)."

        self.applications.set_status(application_id, "Declined", decision_note=reason)

        prop = self.properties.find_by_id(a.property_id)
        self.notifications.emit(
            user_id=a.tenant_id,
            type="lease_application_declined",
            title=f"Application declined — {prop.address if prop else 'Property'}",
            message=f"Your lease application was declined. Reason: {reason}",
            priority="High",
        )
        return True, "Application declined."

    def withdraw(self, application_id: int, session_user: dict):
        a = self.applications.find_by_id(application_id)
        if not a:
            return False, "Application not found."
        if a.tenant_id != session_user.get("user_id"):
            return False, "You can only withdraw your own applications."
        if a.status != "Pending":
            return False, f"Cannot withdraw a {a.status.lower()} application."

        self.applications.set_status(application_id, "Cancelled",
                                      decision_note="Withdrawn by tenant.")
        return True, "Application withdrawn."