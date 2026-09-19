print(">>> lease_service.py V1 <<<")

from datetime import date
from Repositories.lease_repository import LeaseRepository
from Repositories.payment_repository import PaymentRepository
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Models.user import UserRole

WRITE_ROLES = {"Administrator", "Property Manager"}


class LeaseService:
    def __init__(self):
        self.leases = LeaseRepository()
        self.payments = PaymentRepository()
        self.properties = PropertyRepository()
        self.users = UserRepository()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to modify leases."
        return True, None

    def _recalculate_property_status(self, property_id: int):
        """Mirror PropertyService.recalculate_status without circular import."""
        if self.leases.has_active_lease(property_id):
            new_status = "Occupied"
        elif self.properties.has_open_maintenance(property_id):
            new_status = "Under Maintenance"
        else:
            new_status = "Available"
        self.properties.set_status(property_id, new_status)

    @staticmethod
    def _to_dict(lease, property_obj=None, tenant_obj=None):
        return {
            "lease_id": lease.lease_id,
            "property_id": lease.property_id,
            "tenant_id": lease.tenant_id,
            "property_address": property_obj.address if property_obj else "",
            "tenant_name": tenant_obj.name if tenant_obj else "",
            "tenant_email": tenant_obj.email if tenant_obj else "",
            "start_date": lease.start_date,
            "end_date": lease.end_date,
            "rent_amount": lease.rent_amount,
            "status": lease.status,
        }

    def _enrich(self, lease):
        prop = self.properties.find_by_id(lease.property_id)
        tenant = self.users.find_by_id(lease.tenant_id)
        return self._to_dict(lease, prop, tenant)

    # ------------------------------------------------------------------ reads
    def list_leases(self, filters: dict | None = None):
        filters = filters or {}
        status_filter = filters.get("status", "All")
        query = (filters.get("query") or "").strip().lower()

        rows = self.leases.list_all()
        out = []
        for lease in rows:
            d = self._enrich(lease)
            if status_filter and status_filter != "All" and d["status"] != status_filter:
                continue
            if query:
                haystack = f"{d['property_address']} {d['tenant_name']} {d['tenant_email']}".lower()
                if query not in haystack:
                    continue
            out.append(d)
        return out

    def get_lease(self, lease_id: int):
        lease = self.leases.find_by_id(lease_id)
        return self._enrich(lease) if lease else None

    def check_expiring(self, threshold_days: int = 30):
        rows = self.leases.find_expiring(threshold_days)
        return [self._enrich(l) for l in rows]

    # ------------------------------------------------------------------ writes
    def create_lease(self, data: dict, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        try:
            property_id = int(data.get("property_id") or 0)
            tenant_id = int(data.get("tenant_id") or 0)
            rent_amount = float(data.get("rent_amount") or 0)
        except (TypeError, ValueError):
            return False, "Invalid numeric value."

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if rent_amount <= 0:
            return False, "Rent must be greater than zero."
        if not start_date or not end_date:
            return False, "Both start and end dates are required."
        if start_date >= end_date:
            return False, "Start date must be before end date."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        tenant = self.users.find_by_id(tenant_id)
        if not tenant:
            return False, "Tenant not found."
        if tenant.role != UserRole.TENANT:
            return False, "Selected user is not a Tenant."

        if self.leases.has_active_lease(property_id):
            return False, "This property already has an active lease."

        # Create the lease
        lease = self.leases.create(
            property_id=property_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            rent_amount=rent_amount,
        )

        # Generate the first payment
        self.payments.create(
            lease_id=lease.lease_id,
            amount=lease.rent_amount,
            due_date=start_date,
            status="Pending",
        )

        # Update property status
        self._recalculate_property_status(property_id)

        return True, f"Lease #{lease.lease_id} created."

    def terminate_lease(self, lease_id: int, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        lease = self.leases.find_by_id(lease_id)
        if not lease:
            return False, "Lease not found."
        if lease.status != "Active":
            return False, f"Lease is already {lease.status}."

        self.leases.update_status(lease_id, "Terminated")
        self._recalculate_property_status(lease.property_id)
        return True, "Lease terminated."