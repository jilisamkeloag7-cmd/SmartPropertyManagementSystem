print(">>> maintenance_service.py V1 <<<")

from datetime import datetime
from Repositories.maintenance_repository import MaintenanceRepository
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository
from Services.notification_service import NotificationService


VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
VALID_STATUSES   = {"Open", "In Progress", "Resolved", "Closed"}

ALLOWED_TRANSITIONS = {
    "Open":         {"In Progress"},
    "In Progress":  {"Resolved"},
    "Resolved":     {"Closed", "In Progress"},
    "Closed":       set(),
}

MANAGER_ROLES = {"Administrator", "Property Manager"}


class MaintenanceService:
    def __init__(self):
        self.requests = MaintenanceRepository()
        self.properties = PropertyRepository()
        self.leases = LeaseRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()
        self.notifications = NotificationService()

    # ------------------------------------------------------------------ helpers
    def _recalculate_property_status(self, property_id: int):
        if self.leases.has_active_lease(property_id):
            new_status = "Occupied"
        elif self.requests.has_open_request(property_id):
            new_status = "Under Maintenance"
        else:
            new_status = "Available"
        self.properties.set_status(property_id, new_status)

    def _enrich(self, req):
        prop = self.properties.find_by_id(req.property_id)
        submitter = self.users.find_by_id(req.submitted_by)
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

    # ------------------------------------------------------------------ reads
    def list_requests(self, filters: dict | None = None,
                      session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        priority_filter = filters.get("priority", "All")
        query = (filters.get("query") or "").strip().lower()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        # ---- role-based scope
        if role == "Tenant" and uid:
            rows = self.requests.list_for_submitter(uid)
        elif role == "Owner" and uid:
            owned_pids = set(self.ownerships.property_ids_for_owner(uid))
            rows = [r for r in self.requests.list_all()
                    if r.property_id in owned_pids]
        else:
            rows = self.requests.list_all()

        # ---- user filters
        out = []
        for r in rows:
            d = self._enrich(r)
            if status_filter != "All" and d["status"] != status_filter:
                continue
            if priority_filter != "All" and d["priority"] != priority_filter:
                continue
            if query:
                haystack = (
                    f"{d['property_address']} {d['submitter_name']} "
                    f"{d['description']}"
                ).lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_request(self, request_id: int):
        r = self.requests.find_by_id(request_id)
        return self._enrich(r) if r else None

    # ------------------------------------------------------------------ writes
    def submit_request(self, data: dict, session_user: dict):
        """Tenant (or higher) submits a maintenance request for a property
        they have an active lease on."""
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

        # Tenants must have an active lease for the property
        if role == "Tenant":
            my_leases = self.leases.list_for_tenant(uid)
            has_active = any(
                l.property_id == property_id and l.status == "Active"
                for l in my_leases
            )
            if not has_active:
                return False, "You can only report maintenance for properties you lease."

        req = self.requests.create(
            property_id=property_id,
            submitted_by=uid,
            description=description,
            priority=priority,
            status="Open",
        )

        # Recalculate property status (now has an open request)
        self._recalculate_property_status(property_id)

        # Notify managers/owners — for now, notify all admins
        for u in self.users.list_all():
            if u.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    user_id=u.user_id,
                    type="maintenance_new",
                    title="New maintenance request",
                    message=(
                        f"Request #{req.request_id} submitted for "
                        f"{prop.address}: {description[:60]}"
                    ),
                    priority="Normal",
                )

        return True, f"Request #{req.request_id} submitted."

    def update_status(self, request_id: int, new_status: str, session_user: dict):
        # Permission: managers and admins only
        if session_user.get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can update request status."

        if new_status not in VALID_STATUSES:
            return False, f"Invalid status: {new_status}."

        req = self.requests.find_by_id(request_id)
        if not req:
            return False, "Request not found."

        allowed = ALLOWED_TRANSITIONS.get(req.status, set())
        if new_status not in allowed:
            return False, f"Cannot move from {req.status} to {new_status}."

        completed_at = datetime.utcnow() if new_status == "Closed" else None
        self.requests.update_status(request_id, new_status, completed_at)

        # Recalculate property status when request opens or closes
        if new_status in ("Closed", "In Progress", "Resolved"):
            self._recalculate_property_status(req.property_id)

        # Notify the submitter
        self.notifications.emit(
            user_id=req.submitted_by,
            type="maintenance_update",
            title=f"Request #{request_id} → {new_status}",
            message=f"Your maintenance request status changed to '{new_status}'.",
            priority="Normal",
        )

        return True, f"Request #{request_id} → {new_status}."