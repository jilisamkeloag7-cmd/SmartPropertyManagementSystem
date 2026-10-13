
from datetime import date, timedelta
from Services.lease_service import LeaseService
from Services.property_service import PropertyService


def _make_property(admin_session, addr="P Test"):
    ps = PropertyService()
    ps.create_property(
        {"address": addr, "property_type": "House",
         "status": "Available", "build_details": ""},
        admin_session,
    )
    return ps.list_properties({})[0]["property_id"]


def _future_date(days):
    return date.today() + timedelta(days=days)


class TestLeaseService:

    def test_create_lease_generates_payment(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = LeaseService()

        ok, msg = svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(), "end_date": _future_date(365),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        assert ok is True

        # Verify a payment exists
        from Database.connection import get_session
        from Models.payment import Payment
        db = get_session()
        try:
            payments = db.query(Payment).all()
            assert len(payments) == 1
            assert payments[0].amount == 5000.0
        finally:
            db.close()

    def test_create_lease_sets_property_occupied(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = LeaseService()
        svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(), "end_date": _future_date(365),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        ps = PropertyService()
        prop = ps.get_property(pid)
        assert prop["status"] == "Occupied"

    def test_create_lease_blocked_if_active_exists(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = LeaseService()
        svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(), "end_date": _future_date(365),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        ok, msg = svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(), "end_date": _future_date(365),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        assert ok is False
        assert "active lease" in msg.lower()

    def test_create_lease_invalid_dates(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = LeaseService()
        ok, msg = svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": _future_date(10), "end_date": date.today(),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        assert ok is False
        assert "start" in msg.lower()

    def test_terminate_lease_frees_property(self, seeded_db):
        pid = _make_property(seeded_db["admin"])
        svc = LeaseService()
        svc.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(), "end_date": _future_date(365),
             "rent_amount": 5000.0},
            seeded_db["admin"],
        )
        lease_id = svc.list_leases({})[0]["lease_id"]
        ok, _ = svc.terminate_lease(lease_id, seeded_db["admin"])
        assert ok is True

        prop = PropertyService().get_property(pid)
        assert prop["status"] == "Available"
