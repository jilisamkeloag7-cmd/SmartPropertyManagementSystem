print(">>> viewing_service.py V1 <<<")

from datetime import date, datetime, timedelta
from Repositories.viewing_request_repository import ViewingRequestRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Services.notification_service import NotificationService


MANAGER_ROLES = {"Administrator", "Property Manager"}
VALID_TIME_SLOTS = {"Morning", "Afternoon", "Evening"}

# Booking window
MIN_DAYS_AHEAD = 1
MAX_DAYS_AHEAD = 60


class ViewingService:
    def __init__(self):
        self.viewings = ViewingRequestRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()
        self.notifications = NotificationService()

    # ------------------------------------------------------------------ helpers
    def _enrich(self, v):
        prop = self.properties.find_by_id(v.property_id)
        tenant = self.users.find_by_id(v.tenant_id)
        return {
            "request_id": v.request_id,
            "property_id": v.property_id,
            "property_address": prop.address if prop else "",
            "tenant_id": v.tenant_id,
            "tenant_name": tenant.name if tenant else "",
            "tenant_email": tenant.email if tenant else "",
            "preferred_date": v.preferred_date,
            "preferred_time": v.preferred_time or "",
            "message": v.message or "",
            "status": v.status,
            "manager_note": v.manager_note or "",
            "created_at": v.created_at,
            "decided_at": v.decided_at,
        }

    # ------------------------------------------------------------------ reads
    def list_requests(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Tenant" and uid:
            rows = self.viewings.list_for_tenant(uid)
        else:
            rows = self.viewings.list_all()

        out = []
        for v in rows:
            d = self._enrich(v)
            if status_filter and status_filter != "All" and d["status"] != status_filter:
                continue
            if query:
                haystack = f"{d['property_address']} {d['tenant_name']} {d['tenant_email']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_request(self, request_id: int):
        v = self.viewings.find_by_id(request_id)
        return self._enrich(v) if v else None

    def pending_count(self) -> int:
        """For sidebar badge."""
        return sum(1 for v in self.viewings.list_all() if v.status == "Pending")

    # ------------------------------------------------------------------ writes
    def request_viewing(self, property_id: int, preferred_date,
                        preferred_time: str, message: str,
                        session_user: dict):
        role = session_user.get("role", "")
        uid = session_user.get("user_id")

        if role != "Tenant":
            return False, "Only tenants can request viewings."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        if prop.status in ("Archived", "Occupied"):
            return False, f"This property is {prop.status.lower()} — not available for viewings."

        if not preferred_date:
            return False, "Preferred date is required."

        today = date.today()
        if preferred_date < today + timedelta(days=MIN_DAYS_AHEAD):
            return False, f"Preferred date must be at least {MIN_DAYS_AHEAD} day(s) from today."

        if preferred_date > today + timedelta(days=MAX_DAYS_AHEAD):
            return False, f"Preferred date cannot be more than {MAX_DAYS_AHEAD} days away."

        if preferred_time not in VALID_TIME_SLOTS:
            return False, f"Time slot must be one of: {', '.join(sorted(VALID_TIME_SLOTS))}."

        if self.viewings.has_pending_for_property(property_id, uid):
            return False, "You already have a pending viewing request for this property."

        msg = (message or "").strip()
        if len(msg) > 500:
            return False, "Message is too long (max 500 characters)."

        r = self.viewings.create(
            property_id=property_id,
            tenant_id=uid,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            message=msg or None,
        )

        # Notify managers
        for u in self.users.list_all():
            if u.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    user_id=u.user_id,
                    type="viewing_request",
                    title=f"New viewing request — Property #{property_id}",
                    message=(
                        f"{session_user.get('name', 'Tenant')} requested a viewing "
                        f"of {prop.address} on {preferred_date.isoformat()} "
                        f"({preferred_time})."
                    ),
                    priority="Normal",
                )

        return True, f"Viewing request submitted for {preferred_date.isoformat()}."

    def approve(self, request_id: int, manager_note: str, session_user: dict):
        if (session_user or {}).get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can approve viewings."

        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.status != "Pending":
            return False, f"Request is already {v.status}."

        note = (manager_note or "").strip()
        self.viewings.set_status(request_id, "Approved", note or None)

        prop = self.properties.find_by_id(v.property_id)
        self.notifications.emit(
            user_id=v.tenant_id,
            type="viewing_approved",
            title=f"Viewing approved — {prop.address if prop else 'Property'}",
            message=(
                f"Your viewing request for {v.preferred_date.isoformat()} "
                f"({v.preferred_time}) has been approved."
                + (f" Note from management: {note}" if note else "")
            ),
            priority="Normal",
        )
        return True, "Viewing approved."

    def decline(self, request_id: int, reason: str, session_user: dict):
        if (session_user or {}).get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can decline viewings."

        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.status != "Pending":
            return False, f"Request is already {v.status}."

        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason (at least 3 characters)."

        self.viewings.set_status(request_id, "Declined", reason)

        prop = self.properties.find_by_id(v.property_id)
        self.notifications.emit(
            user_id=v.tenant_id,
            type="viewing_declined",
            title=f"Viewing declined — {prop.address if prop else 'Property'}",
            message=(
                f"Your viewing request for {v.preferred_date.isoformat()} "
                f"was declined. Reason: {reason}"
            ),
            priority="Normal",
        )
        return True, "Viewing declined."

    def cancel(self, request_id: int, session_user: dict):
        """Tenant cancels their own pending request."""
        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.tenant_id != session_user.get("user_id"):
            return False, "You can only cancel your own requests."
        if v.status != "Pending":
            return False, f"Cannot cancel a {v.status.lower()} request."

        self.viewings.set_status(request_id, "Cancelled")
        return True, "Viewing request cancelled."