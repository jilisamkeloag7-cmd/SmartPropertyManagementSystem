print(">>> property_service.py V2 <<<")

from Repositories.property_repository import PropertyRepository

VALID_TYPES = {"House", "Apartment", "Commercial", "Other"}
VALID_STATUSES = {"Available", "Occupied", "Under Maintenance", "Archived"}
WRITE_ROLES = {"Administrator", "Property Manager"}


class PropertyService:
    def __init__(self):
        self.properties = PropertyRepository()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to modify properties."
        return True, None

    @staticmethod
    def _parse_price(raw):
        """Return (ok, price_or_error). Empty → None (unset)."""
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
        if data.get("status") not in VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."
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

    # ------------------------------------------------------------------ writes
    def create_property(self, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err
        ok, err = self._validate(data)
        if not ok:
            return False, err

        _, price = self._parse_price(data.get("listing_price"))
        p = self.properties.create(
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=data["status"],
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

        _, price = self._parse_price(data.get("listing_price"))
        p = self.properties.update(
            property_id=property_id,
            address=data["address"].strip(),
            property_type=data["property_type"],
            build_details=(data.get("build_details") or "").strip(),
            status=data["status"],
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

    # ------------------------------------------------------------------ status
    def recalculate_status(self, property_id: int) -> str:
        if self.properties.has_active_lease(property_id):
            new_status = "Occupied"
        elif self.properties.has_open_maintenance(property_id):
            new_status = "Under Maintenance"
        else:
            new_status = "Available"
        self.properties.set_status(property_id, new_status)
        return new_status