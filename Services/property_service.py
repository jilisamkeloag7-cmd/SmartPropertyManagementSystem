print(">>> property_service.py V3 <<<")

from Repositories.property_repository import PropertyRepository
from Repositories.ownership_repository import OwnershipRepository


VALID_TYPES = {"House", "Apartment", "Commercial", "Other"}
VALID_STATUSES = {"Available", "Occupied", "Under Maintenance", "Archived",
                  "Pending Approval", "Rejected"}
WRITE_ROLES = {"Administrator", "Property Manager"}
OWNER_ROLE = "Owner"

# Owner-submitted properties enter this state automatically
PENDING_STATUS = "Pending Approval"


class PropertyService:
    def __init__(self):
        self.properties = PropertyRepository()
        self.ownerships = OwnershipRepository()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to modify properties."
        return True, None

    @staticmethod
    def _assert_admin(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "Only managers or administrators can approve properties."
        return True, None

    @staticmethod
    def _parse_price(raw):
        if raw in (None, ""):
            return True, None
        try:
            val = float(raw)
        except (TypeError, ValueError):
            return False, "Listing price must be a number."
        if val < 0:
            return False, "Listing price cannot be negative."
        if val > 1_000_000:
            return False, "Listing price looks unrealistic (over R1,000,000)."
        return True, val

    def _validate(self, data):
        address = (data.get("address") or "").strip()
        if not address:
            return False, "Address is required."
        if data.get("property_type") not in VALID_TYPES:
            return False, f"Property type must be one of: {', '.join(sorted(VALID_TYPES))}."
        ok, price_or_err = self._parse_price(data.get("listing_price"))
        if not ok:
            return False, price_or_err
        return True, None

    @staticmethod
    def _to_dict(p):
        return {
            "property_id": p.property_id,
            "address": p.address,
            "property_type": p.property_type,
            "build_details": p.build_details,
            "status": p.status,
            "listing_price": p.listing_price,
            "created_at": p.created_at,
        }

    # ------------------------------------------------------------------ reads
    def list_properties(self, filters: dict | None = None):
        filters = filters or {}
        rows = self.properties.search(
            query=filters.get("query", ""),
            status_filter=filters.get("status", "All"),
        )
        return [self._to_dict(p) for p in rows]

    def get_property(self, property_id: int):
        p = self.properties.find_by_id(property_id)
        return self._to_dict(p) if p else None

    # ------------------------------------------------------------------ writes — writers (admin/manager)
    def create_property(self, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err
        ok, err = self._validate(data)
        if not ok:
            return False, err

        status = data.get("status", "Available")
        if status not in VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."

        _, price = self._parse_price(data.get("listing_price"))
        p = self.properties.create(
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=status,
            listing_price=price,
        )
        return True, f"Property #{p.property_id} created."

    def update_property(self, property_id: int, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err
        ok, err = self._validate(data)
        if not ok:
            return False, err

        status = data.get("status", "Available")
        if status not in VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."

        _, price = self._parse_price(data.get("listing_price"))
        p = self.properties.update(
            property_id=property_id,
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=status,
            listing_price=price,
        )
        if not p:
            return False, "Property not found."
        return True, "Property updated."

    def archive_property(self, property_id: int, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err
        if self.properties.has_active_lease(property_id):
            return False, "Cannot archive: property has an active lease."
        ok = self.properties.set_status(property_id, "Archived")
        return (True, "Property archived.") if ok else (False, "Property not found.")

    # ------------------------------------------------------------------ owner submission
    def owner_submit_property(self, data: dict, session_user: dict):
        """Owner submits a new property. Status auto-set to Pending Approval.
        An Ownership record is created immediately so the owner owns it once approved."""
        role = session_user.get("role", "")
        uid = session_user.get("user_id")

        if role != OWNER_ROLE:
            return False, "Only owners can submit properties for approval."

        ok, err = self._validate(data)
        if not ok:
            return False, err

        _, price = self._parse_price(data.get("listing_price"))
        prop = self.properties.create(
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=PENDING_STATUS,
            listing_price=price,
        )

        # Auto-assign ownership
        try:
            self.ownerships.create(
                property_id=prop.property_id,
                user_id=uid,
                share=1.0,
                start_date=None,   # will be set on approval
            )
        except Exception:
            pass   # Ownership already exists or user has no ownership yet — non-fatal

        return True, (
            f"Property #{prop.property_id} submitted for approval. "
            f"You'll be notified once a manager reviews it."
        )

    def owner_update_property(self, property_id: int, data: dict, session_user: dict):
        """Owner edits their own pending property. Cannot change status."""
        role = session_user.get("role", "")
        uid = session_user.get("user_id")

        if role != OWNER_ROLE:
            return False, "Only owners can use this action."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        # Verify ownership
        owned = set(self.ownerships.property_ids_for_owner(uid))
        if property_id not in owned:
            return False, "You can only edit your own properties."

        # Only allow editing while pending
        if prop.status not in (PENDING_STATUS, "Rejected"):
            return False, f"Cannot edit a property with status '{prop.status}'."

        ok, err = self._validate(data)
        if not ok:
            return False, err

        _, price = self._parse_price(data.get("listing_price"))
        # Keep status — owner cannot change it
        self.properties.update(
            property_id=property_id,
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=prop.status,
            listing_price=price,
        )
        return True, "Property updated. Awaiting manager review."

    def owner_withdraw_property(self, property_id: int, session_user: dict):
        """Owner removes a pending submission."""
        role = session_user.get("role", "")
        uid = session_user.get("user_id")
        if role != OWNER_ROLE:
            return False, "Only owners can use this action."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."
        if prop.status not in (PENDING_STATUS, "Rejected"):
            return False, "Only pending or rejected properties can be withdrawn."

        owned = set(self.ownerships.property_ids_for_owner(uid))
        if property_id not in owned:
            return False, "You can only withdraw your own properties."

        self.properties.set_status(property_id, "Archived")
        return True, "Submission withdrawn."

    # ------------------------------------------------------------------ approval
    def approve_property(self, property_id: int, session_user: dict):
        """Admin or Manager approves a pending property submission."""
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."
        if prop.status != PENDING_STATUS:
            return False, f"Property is not pending — status: {prop.status}."

        self.properties.set_status(property_id, "Available")

        # Notify the owner(s)
        from Services.notification_service import NotificationService
        notifier = NotificationService()
        for o in self.ownerships.list_for_property(property_id):
            notifier.emit(
                user_id=o.user_id,
                type="property_approved",
                title=f"Property approved — {prop.address}",
                message=f"Your property submission #{property_id} has been approved.",
                priority="Normal",
            )

        return True, f"Property #{property_id} approved and now Available."

    def reject_property(self, property_id: int, reason: str, session_user: dict):
        """Admin or Manager rejects a pending property submission."""
        ok, err = self._assert_admin(session_user)
        if not ok:
            return False, err

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."
        if prop.status != PENDING_STATUS:
            return False, f"Property is not pending — status: {prop.status}."

        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason (at least 3 characters)."

        self.properties.set_status(property_id, "Rejected")

        from Services.notification_service import NotificationService
        notifier = NotificationService()
        for o in self.ownerships.list_for_property(property_id):
            notifier.emit(
                user_id=o.user_id,
                type="property_rejected",
                title=f"Property rejected — {prop.address}",
                message=f"Your submission for {prop.address} was declined. Reason: {reason}",
                priority="High",
            )

        return True, f"Property #{property_id} rejected."

    # ------------------------------------------------------------------ status
    def recalculate_status(self, property_id: int) -> str:
        prop = self.properties.find_by_id(property_id)
        if not prop:
            return ""
        # Do not auto-update while pending or rejected
        if prop.status in (PENDING_STATUS, "Rejected"):
            return prop.status

        if self.properties.has_active_lease(property_id):
            new_status = "Occupied"
        elif self.properties.has_open_maintenance(property_id):
            new_status = "Under Maintenance"
        else:
            new_status = "Available"
        self.properties.set_status(property_id, new_status)
        return new_status