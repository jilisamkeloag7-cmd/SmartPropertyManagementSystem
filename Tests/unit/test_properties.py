
import pytest
from Services.property_service import PropertyService


class TestPropertyService:

    def test_create_as_admin(self, seeded_db):
        svc = PropertyService()
        ok, msg = svc.create_property(
            {"address": "10 Test Rd", "property_type": "House",
             "status": "Available", "build_details": "3 bed"},
            seeded_db["admin"],
        )
        assert ok is True
        assert "created" in msg.lower()

    def test_create_requires_address(self, seeded_db):
        svc = PropertyService()
        ok, msg = svc.create_property(
            {"address": "  ", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        assert ok is False
        assert "Address is required" in msg

    def test_create_tenant_forbidden(self, seeded_db):
        svc = PropertyService()
        ok, msg = svc.create_property(
            {"address": "X", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["tenant"],
        )
        assert ok is False
        assert "permission" in msg.lower()

    def test_update_property(self, seeded_db):
        svc = PropertyService()
        svc.create_property(
            {"address": "1 Old", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        props = svc.list_properties({})
        pid = props[0]["property_id"]

        ok, msg = svc.update_property(
            pid,
            {"address": "1 New", "property_type": "Apartment",
             "status": "Available", "build_details": "upd"},
            seeded_db["admin"],
        )
        assert ok is True
        updated = svc.get_property(pid)
        assert updated["address"] == "1 New"
        assert updated["property_type"] == "Apartment"

    def test_archive_blocked_when_active_lease(self, seeded_db):
        from Services.property_service import PropertyService as PS
        from Services.lease_service import LeaseService

        ps = PS()
        ps.create_property(
            {"address": "P1", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        pid = ps.list_properties({})[0]["property_id"]

        ls = LeaseService()
        ls.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": __import__("datetime").date.today(),
             "end_date": __import__("datetime").date.today().replace(year=2027),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )

        ok, msg = ps.archive_property(pid, seeded_db["admin"])
        assert ok is False
        assert "active lease" in msg.lower()
