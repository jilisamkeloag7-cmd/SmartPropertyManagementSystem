
from datetime import date, timedelta
from Repositories.viewing_request_repository import ViewingRequestRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService
from Database.connection import get_session
from Models.property import Property
from Models.user import User


MANAGER_ROLES = {"Administrator", "Property Manager"}
VALID_TIME_SLOTS = {"Morning", "Afternoon", "Evening"}
MIN_DAYS_AHEAD = 1
MAX_DAYS_AHEAD = 60


class ViewingService:
    def __init__(self):
        self.viewings = ViewingRequestRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()
        self.notifications = NotificationService()

    @staticmethod
    def _prefetch():
        db = get_session()
        try:
            props = {p.property_id: p for p in db.query(Property).all()}
            users = {u.user_id: u for u in db.query(User).all()}
            return props, users
        finally:
            db.close()

    def _enrich(self, v, props_by_id, users_by_id):
        prop = props_by_id.get(v.property_id)
        tenant = users_by_id.get(v.tenant_id)
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

    def _enrich_one(self, v):
        prop = self.properties.find_by_id(v.property_id)
        tenant = self.users.find_by_id(v.tenant_id)
        return self._enrich(v,
                            {v.property_id: prop} if prop else {},
                            {v.tenant_id: tenant} if tenant else {})

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
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            rows = [v for v in self.viewings.list_all() if v.property_id in owned_pids]
        else:
            rows = self.viewings.list_all()

        props_by_id, users_by_id = self._prefetch()

        out = []
        for v in rows:
            d = self._enrich(v, props_by_id, users_by_id)
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
        return self._enrich_one(v) if v else None

    def pending_count(self) -> int:
        return sum(1 for v in self.viewings.list_all() if v.status == "Pending")

    # ------------------------------------------------------------------ writes
    def request_viewing(self, property_id, preferred_date, preferred_time,
                        message, session_user):
        role = session_user.get("role", "")
        uid = session_user.get("user_id")
        if role != "Tenant":
            return False, "Only tenants can request viewings."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."
        if prop.status in ("Archived", "Occupied"):
            return False, f"This property is {prop.status.lower()} — not available."

        if not preferred_date:
            return False, "Preferred date is required."

        today = date.today()
        if preferred_date < today + timedelta(days=MIN_DAYS_AHEAD):
            return False, f"Date must be at least {MIN_DAYS_AHEAD} day(s) away."
        if preferred_date > today + timedelta(days=MAX_DAYS_AHEAD):
            return False, f"Date cannot be more than {MAX_DAYS_AHEAD} days away."
        if preferred_time not in VALID_TIME_SLOTS:
            return False, f"Time must be one of: {', '.join(sorted(VALID_TIME_SLOTS))}."

        if self.viewings.has_pending_for_property(property_id, uid):
            return False, "You already have a pending request for this property."

        msg = (message or "").strip()
        if len(msg) > 500:
            return False, "Message too long."

        r = self.viewings.create(property_id, uid, preferred_date,
                                  preferred_time, msg or None)

        for u in self.users.list_all():
            if u.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    u.user_id, "viewing_request",
                    f"New viewing request — Property #{property_id}",
                    f"{session_user.get('name', 'Tenant')} requested a viewing "
                    f"of {prop.address} on {preferred_date.isoformat()} "
                    f"({preferred_time}).",
                    "Normal",
                )
        return True, f"Viewing request submitted."

    def approve(self, request_id, manager_note, session_user):
        if session_user.get("role") not in MANAGER_ROLES:
            return False, "Only managers can approve."
        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.status != "Pending":
            return False, f"Already {v.status}."
        note = (manager_note or "").strip()
        self.viewings.set_status(request_id, "Approved", note or None)
        prop = self.properties.find_by_id(v.property_id)
        self.notifications.emit(
            v.tenant_id, "viewing_approved",
            f"Viewing approved — {prop.address if prop else 'Property'}",
            f"Your viewing on {v.preferred_date.isoformat()} ({v.preferred_time}) "
            f"was approved." + (f" Note: {note}" if note else ""),
            "Normal",
        )
        return True, "Viewing approved."

    def decline(self, request_id, reason, session_user):
        if session_user.get("role") not in MANAGER_ROLES:
            return False, "Only managers can decline."
        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.status != "Pending":
            return False, f"Already {v.status}."
        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason."
        self.viewings.set_status(request_id, "Declined", reason)
        prop = self.properties.find_by_id(v.property_id)
        self.notifications.emit(
            v.tenant_id, "viewing_declined",
            f"Viewing declined — {prop.address if prop else 'Property'}",
            f"Your viewing request was declined. Reason: {reason}",
            "Normal",
        )
        return True, "Viewing declined."

    def cancel(self, request_id, session_user):
        v = self.viewings.find_by_id(request_id)
        if not v:
            return False, "Request not found."
        if v.tenant_id != session_user.get("user_id"):
            return False, "You can only cancel your own requests."
        if v.status != "Pending":
            return False, f"Cannot cancel a {v.status.lower()} request."
        self.viewings.set_status(request_id, "Cancelled")
        return True, "Viewing request cancelled."
