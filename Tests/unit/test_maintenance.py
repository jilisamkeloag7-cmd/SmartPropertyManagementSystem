
from datetime import date, timedelta
from Services.property_service import PropertyService
from Services.lease_service import LeaseService
from Services.maintenance_service import MaintenanceService


def _setup_leased_property(admin, tenant_id):
    ps = PropertyService()
    ps.create_property(
        {"address": "MP", "property_type": "House",
         "status": "Available", "build_details": ""},
        admin,
    )
    pid = ps.list_properties({})[0]["property_id"]
    ls = LeaseService()
    ls.create_lease(
        {"property_id": pid, "tenant_id": tenant_id,
         "start_date": date.today(), "end_date": date.today() + timedelta(days=365),
         "rent_amount": 5000.0},
        admin,
    )
    return pid


class TestMaintenanceService:

    def test_submit_request_creates_open(self, seeded_db):
        pid = _setup_leased_property(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = MaintenanceService()
        ok, msg = svc.submit_request(
            {"property_id": pid, "priority": "High",
             "description": "Leaking tap in kitchen"},
            seeded_db["tenant"],
        )
        assert ok is True
        req = svc.list_requests({}, seeded_db["tenant"])[0]
        assert req["status"] == "Open"
        assert req["priority"] == "High"

    def test_status_transition_valid(self, seeded_db):
        pid = _setup_leased_property(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = MaintenanceService()
        svc.submit_request(
            {"property_id": pid, "priority": "Medium", "description": "issue"},
            seeded_db["tenant"],
        )
        rid = svc.list_requests({}, seeded_db["tenant"])[0]["request_id"]

        ok, _ = svc.update_status(rid, "In Progress", seeded_db["admin"])
        assert ok is True

    def test_status_transition_invalid_rejected(self, seeded_db):
        pid = _setup_leased_property(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = MaintenanceService()
        svc.submit_request(
            {"property_id": pid, "priority": "Low", "description": "issue"},
            seeded_db["tenant"],
        )
        rid = svc.list_requests({}, seeded_db["tenant"])[0]["request_id"]

        # Open → Closed is not allowed
        ok, msg = svc.update_status(rid, "Closed", seeded_db["admin"])
        assert ok is False

    def test_tenant_can_only_submit_for_leased_property(self, seeded_db):
        # Create a property with no lease for the tenant
        ps = PropertyService()
        ps.create_property(
            {"address": "NoLease", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        pid = ps.list_properties({})[0]["property_id"]

        svc = MaintenanceService()
        ok, msg = svc.submit_request(
            {"property_id": pid, "priority": "Medium", "description": "x"},
            seeded_db["tenant"],
        )
        assert ok is False
        assert "lease" in msg.lower()
