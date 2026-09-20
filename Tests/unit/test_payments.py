print(">>> test_payments.py <<<")

from datetime import date, timedelta
from Services.property_service import PropertyService
from Services.lease_service import LeaseService
from Services.payment_service import PaymentService


def _setup_lease(admin, tenant_id):
    ps = PropertyService()
    ps.create_property(
        {"address": "PayP", "property_type": "House",
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
    return ls.list_leases({})[0]["lease_id"]


class TestPaymentService:

    def test_mark_paid(self, seeded_db):
        lease_id = _setup_lease(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = PaymentService()
        payments = svc.list_payments({}, seeded_db["admin"])
        pid = payments[0]["payment_id"]

        ok, _ = svc.mark_paid(pid, date.today(), seeded_db["admin"])
        assert ok is True

        updated = svc.get_payment(pid)
        assert updated["status"] == "Paid"
        assert updated["paid_date"] == date.today()

    def test_mark_paid_twice_rejected(self, seeded_db):
        lease_id = _setup_lease(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = PaymentService()
        pid = svc.list_payments({}, seeded_db["admin"])[0]["payment_id"]
        svc.mark_paid(pid, date.today(), seeded_db["admin"])

        ok, msg = svc.mark_paid(pid, date.today(), seeded_db["admin"])
        assert ok is False
        assert "already" in msg.lower()

    def test_check_overdue_flips_past_pending(self, seeded_db):
        lease_id = _setup_lease(seeded_db["admin"], seeded_db["tenant"]["user_id"])

        # Backdate the payment to 5 days ago
        from Database.connection import get_session
        from Models.payment import Payment
        db = get_session()
        try:
            p = db.query(Payment).first()
            p.due_date = date.today() - timedelta(days=5)
            db.commit()
            pid = p.payment_id
        finally:
            db.close()

        svc = PaymentService()
        newly = svc.check_overdue()
        assert newly >= 1

        p = svc.get_payment(pid)
        assert p["status"] == "Overdue"

    def test_tenant_only_sees_own_payments(self, seeded_db):
        lease_id = _setup_lease(seeded_db["admin"], seeded_db["tenant"]["user_id"])
        svc = PaymentService()

        admin_view = svc.list_payments({}, seeded_db["admin"])
        assert len(admin_view) == 1

        # Owner (not on this lease) should see nothing
        owner_view = svc.list_payments({}, seeded_db["owner"])
        assert len(owner_view) == 0

        tenant_view = svc.list_payments({}, seeded_db["tenant"])
        assert len(tenant_view) == 1