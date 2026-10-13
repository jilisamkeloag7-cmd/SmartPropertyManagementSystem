
from datetime import date
from Services.property_service import PropertyService
from Services.ownership_service import OwnershipService


def _make_property(admin, addr="OP"):
    ps = PropertyService()
    ps.create_property(
        {"address": addr, "property_type": "House",
         "status": "Available", "build_details": ""},
        admin,
    )
    return ps.list_properties({})[0]["property_id"]


class TestOwnershipService:

    def test_add_valid(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = OwnershipService()
        ok, _ = svc.add_ownership(
            {"property_id": pid, "user_id": seeded_db["owner"]["user_id"],
             "ownership_share": 1.0, "start_date": date.today(),
             "end_date": None},
            seeded_db["admin"],
        )
        assert ok is True

    def test_add_exceeding_100_rejected(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = OwnershipService()
        svc.add_ownership(
            {"property_id": pid, "user_id": seeded_db["owner"]["user_id"],
             "ownership_share": 0.7, "start_date": date.today(), "end_date": None},
            seeded_db["admin"],
        )
        # Try to add 0.6 → should exceed 100%
        ok, msg = svc.add_ownership(
            {"property_id": pid, "user_id": seeded_db["owner"]["user_id"],
             "ownership_share": 0.6, "start_date": date.today(), "end_date": None},
            seeded_db["admin"],
        )
        assert ok is False
        assert "100" in msg

    def test_add_requires_owner_role(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = OwnershipService()
        ok, msg = svc.add_ownership(
            {"property_id": pid, "user_id": seeded_db["tenant"]["user_id"],
             "ownership_share": 0.5, "start_date": date.today(), "end_date": None},
            seeded_db["admin"],
        )
        assert ok is False
        assert "owner" in msg.lower()

    def test_end_ownership_soft_closes(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = OwnershipService()
        svc.add_ownership(
            {"property_id": pid, "user_id": seeded_db["owner"]["user_id"],
             "ownership_share": 1.0, "start_date": date.today(), "end_date": None},
            seeded_db["admin"],
        )
        oid = svc.list_ownerships({}, seeded_db["admin"])[0]["ownership_id"]
        ok, _ = svc.end_ownership(oid, seeded_db["admin"])
        assert ok is True

        ended = svc.get_ownership(oid)
        assert ended["is_active"] is False
        assert ended["end_date"] is not None
