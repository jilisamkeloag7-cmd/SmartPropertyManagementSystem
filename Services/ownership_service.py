
from datetime import date
from Repositories.ownership_repository import OwnershipRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Database.connection import get_session
from Models.property import Property
from Models.user import User
from Models.user import UserRole


WRITE_ROLES = {"Administrator", "Property Manager"}


class OwnershipService:
    def __init__(self):
        self.ownerships = OwnershipRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()

    @staticmethod
    def _prefetch():
        db = get_session()
        try:
            props = {p.property_id: p for p in db.query(Property).all()}
            users = {u.user_id: u for u in db.query(User).all()}
            return props, users
        finally:
            db.close()

    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to modify ownership."
        return True, None

    def _enrich(self, o, props_by_id, users_by_id):
        prop = props_by_id.get(o.property_id)
        owner = users_by_id.get(o.user_id)
        return {
            "ownership_id": o.ownership_id,
            "property_id": o.property_id,
            "property_address": prop.address if prop else "",
            "user_id": o.user_id,
            "owner_name": owner.name if owner else "",
            "owner_email": owner.email if owner else "",
            "ownership_share": o.ownership_share,
            "start_date": o.start_date,
            "end_date": o.end_date,
            "is_active": o.end_date is None,
        }

    def _enrich_one(self, o):
        prop = self.properties.find_by_id(o.property_id)
        owner = self.users.find_by_id(o.user_id)
        return self._enrich(o,
                            {o.property_id: prop} if prop else {},
                            {o.user_id: owner} if owner else {})

    def list_ownerships(self, filters: dict | None = None,
                        session_user: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        role = (session_user or {}).get("role", "")
        uid = (session_user or {}).get("user_id")

        if role == "Owner" and uid:
            rows = self.ownerships.list_for_owner(uid)
        else:
            rows = self.ownerships.list_all()

        props_by_id, users_by_id = self._prefetch()

        out = []
        for o in rows:
            d = self._enrich(o, props_by_id, users_by_id)
            if status_filter == "Active" and not d["is_active"]:
                continue
            if status_filter == "Ended" and d["is_active"]:
                continue
            if query:
                haystack = f"{d['property_address']} {d['owner_name']} {d['owner_email']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_ownership(self, ownership_id: int):
        o = self.ownerships.find_by_id(ownership_id)
        return self._enrich_one(o) if o else None

    def share_total(self, property_id: int) -> float:
        return self.ownerships.sum_active_shares(property_id)

    def add_ownership(self, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        try:
            property_id = int(data.get("property_id") or 0)
            user_id = int(data.get("user_id") or 0)
            share = float(data.get("ownership_share") or 0)
        except (TypeError, ValueError):
            return False, "Invalid numeric value."

        start_date = data.get("start_date") or date.today()
        end_date = data.get("end_date")

        if share <= 0 or share > 1.0:
            return False, "Ownership share must be between 0 and 1.0."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        user = self.users.find_by_id(user_id)
        if not user:
            return False, "User not found."
        if user.role != UserRole.OWNER:
            return False, "Only users with the Owner role can be assigned ownership."

        active_total = self.ownerships.sum_active_shares(property_id)
        if active_total + share > 1.0 + 1e-9:
            return False, (
                f"Shares exceed 100%. Allocated: {active_total * 100:.0f}%. "
                f"Adding {share * 100:.0f}% would exceed 100%."
            )

        o = self.ownerships.create(
            property_id=property_id, user_id=user_id, share=share,
            start_date=start_date, end_date=end_date,
        )
        return True, f"Ownership #{o.ownership_id} created."

    def end_ownership(self, ownership_id: int, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        o = self.ownerships.find_by_id(ownership_id)
        if not o:
            return False, "Ownership record not found."
        if o.end_date is not None:
            return False, "Ownership is already closed."

        self.ownerships.close(ownership_id, date.today())
        return True, "Ownership ended today."
