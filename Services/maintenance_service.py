
from datetime import datetime
from Repositories.maintenance_repository import MaintenanceRepository
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService
from Database.connection import get_session
from Models.property import Property
from Models.user import User


VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
VALID_STATUSES   = {"Open", "In Progress", "Resolved", "Closed"}
ALLOWED_TRANSITIONS = {
    "Open":         {"In Progress"},
    "In Progress":  {"Resolved"},
    "Resolved":     {"Closed", "In Progress"},
    "Closed":       set(),
}
MANAGER_ROLES       = {"Administrator", "Property Manager"}
STATUS_CHANGE_ROLES = {"Administrator", "Property Manager", "Owner"}


class MaintenanceService:
    def __init__(self):
        self.requests = MaintenanceRepository()
        self.properties = PropertyRepository()
        self.leases = LeaseRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()
        self.notifications = NotificationService()

    @staticmethod
    def _prefetch_lookups():
        db = get_session()
        try:
            props = {p.property_id: p for p in db.query(Property).all()}
            users = {u.user_id: u for u in db.query(User).all()}
            return props, users
        finally:
            db.close()

    def _recalculate_property_status(self, property_id: int):
        if self.leases.has_active_lease(property_id):
            new_status = "Occupied"
        elif self.requests.has_open_request(property_id):
            new_status = "Under Maintenance"
        else:
            new_status = "Available"
        self.properties.set_status(property_id, new_status)

    def _enrich(self, req, props_by_id, users_by_id):
        prop = props_by_id.get(req.property_id)
        submitter = users_by_id.get(req.submitted_by)
        return {
            "request_id": req.request_id,
            "property_id": req.property_id,
            "property_address": prop.address if prop else "",
            "submitted_by": req.submitted_by,
            "submitter_name": submitter.name if submitter else "",
            "submitter_email": submitter.email if submitter else "",
            "description": req.description,
            "priority": req.priority,
            "status": req.status,
            "created_at": req.created_at,
            "completed_at": req.completed_at,
        }

    def _enrich_one(self, req):
        prop = self.properties.find_by_id(req.property_id)
        submitter = self.users.find_by_id(req.submitted_by)
        return self._enrich(req, 
                            {req.property_id: prop} if prop else {},
                            {req.submitted_by: submitter} if submitter else {})

    # ------------------------------------------------------------------ reads
    def list_requests(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        priority_filter = filters.get("priority", "All")
        query = (filters.get("query") or "").strip().lower()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Tenant" and uid:
            rows = self.requests.list_for_submitter(uid)
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            rows = [r for r in self.requests.list_all() if r.property_id in owned_pids]
        else:
            rows = self.requests.list_all()

        props_by_id, users_by_id = self._prefetch_lookups()

        out = []
        for r in rows:
            d = self._enrich(r, props_by_id, users_by_id)
            if status_filter != "All" and d["status"] != status_filter:
                continue
            if priority_filter != "All" and d["priority"] != priority_filter:
                continue
            if query:
                haystack = f"{d['property_address']} {d['submitter_name']} {d['description']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_request(self, request_id: int):
        r = self.requests.find_by_id(request_id)
        return self._enrich_one(r) if r else None

    # ------------------------------------------------------------------ writes
    def submit_request(self, data: dict, session_user: dict):
        try:
            property_id = int(data.get("property_id") or 0)
        except (TypeError, ValueError):
            return False, "Invalid property."

        description = (data.get("description") or "").strip()
        priority = data.get("priority", "Medium")

        if not description:
            return False, "Description is required."
        if priority not in VALID_PRIORITIES:
            return False, f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        uid = session_user.get("user_id")
        role = session_user.get("role", "")

        if role == "Tenant":
            my_leases = self.leases.list_for_tenant(uid)
            has_active = any(l.property_id == property_id and l.status == "Active"
                             for l in my_leases)
            if not has_active:
                return False, "You can only report maintenance for properties you lease."

        if role == "Owner":
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            if property_id not in owned_pids:
                return False, "You can only report maintenance on properties you own."

        req = self.requests.create(
            property_id=property_id, submitted_by=uid,
            description=description, priority=priority, status="Open",
        )
        self._recalculate_property_status(property_id)

        for u in self.users.list_all():
            if u.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    u.user_id, "maintenance_new",
                    "New maintenance request",
                    f"Request #{req.request_id} submitted for {prop.address}: "
                    f"{description[:60]}",
                    "Normal",
                )
        return True, f"Request #{req.request_id} submitted."

    def update_status(self, request_id: int, new_status: str, session_user: dict):
        role = session_user.get("role", "")
        if role not in STATUS_CHANGE_ROLES:
            return False, "Only managers, admins, or owners can update status."
        if new_status not in VALID_STATUSES:
            return False, f"Invalid status: {new_status}."

        req = self.requests.find_by_id(request_id)
        if not req:
            return False, "Request not found."

        if role == "Owner":
            uid = session_user.get("user_id")
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            if req.property_id not in owned_pids:
                return False, "You may only update requests on your own properties."

        allowed = ALLOWED_TRANSITIONS.get(req.status, set())
        if new_status not in allowed:
            return False, f"Cannot move from {req.status} to {new_status}."

        completed_at = datetime.utcnow() if new_status == "Closed" else None
        self.requests.update_status(request_id, new_status, completed_at)

        if new_status in ("Closed", "In Progress", "Resolved"):
            self._recalculate_property_status(req.property_id)

        self.notifications.emit(
            req.submitted_by, "maintenance_update",
            f"Request #{request_id} → {new_status}",
            f"Your maintenance request status changed to '{new_status}'.",
            "Normal",
        )
        return True, f"Request #{request_id} → {new_status}."
