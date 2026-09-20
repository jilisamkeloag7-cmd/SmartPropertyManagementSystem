print(">>> test_lease_lifecycle.py <<<")

from datetime import date, timedelta
from Services.property_service import PropertyService
from Services.lease_service import LeaseService
from Services.payment_service import PaymentService


class TestLeaseLifecycle:

    def test_create_lease_then_check_property_and_payment(self, seeded_db):
        # 1. Create property
        ps = PropertyService()
        ps.create_property(
            {"address": "LC1", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        pid = ps.list_properties({})[0]["property_id"]
        assert ps.get_property(pid)["status"] == "Available"

        # 2. Create lease
        ls = LeaseService()
        ok, _ = ls.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(),
             "end_date": date.today() + timedelta(days=180),
             "rent_amount": 7500.0},
            seeded_db["admin"],
        )
        assert ok is True

        # 3. Property now Occupied
        assert ps.get_property(pid)["status"] == "Occupied"

        # 4. Payment was auto-created
        payments = PaymentService().list_payments({}, seeded_db["admin"])
        assert len(payments) == 1
        assert payments[0]["amount"] == 7500.0
        assert payments[0]["status"] == "Pending"

    def test_terminate_lease_reverts_property(self, seeded_db):
        ps = PropertyService()
        ps.create_property(
            {"address": "LC2", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        pid = ps.list_properties({})[0]["property_id"]

        ls = LeaseService()
        ls.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today(),
             "end_date": date.today() + timedelta(days=180),
             "rent_amount": 7500.0},
            seeded_db["admin"],
        )
        lease_id = ls.list_leases({})[0]["lease_id"]

        ok, _ = ls.terminate_lease(lease_id, seeded_db["admin"])
        assert ok is True
        assert ps.get_property(pid)["status"] == "Available"

    def test_payment_overdue_full_chain(self, seeded_db):
        # Setup lease
        ps = PropertyService()
        ps.create_property(
            {"address": "LC3", "property_type": "House",
             "status": "Available", "build_details": ""},
            seeded_db["admin"],
        )
        pid = ps.list_properties({})[0]["property_id"]
        ls = LeaseService()
        ls.create_lease(
            {"property_id": pid, "tenant_id": seeded_db["tenant"]["user_id"],
             "start_date": date.today() - timedelta(days=10),
             "end_date": date.today() + timedelta(days=355),
             "rent_amount": 6000.0},
            seeded_db["admin"],
        )

        # Backdate the payment
        from Database.connection import get_session
        from Models.payment import Payment
        db = get_session()
        try:
            p = db.query(Payment).first()
            p.due_date = date.today() - timedelta(days=3)
            db.commit()
        finally:
            db.close()

        # Run overdue check
        newly = PaymentService().check_overdue()
        assert newly == 1

        # Verify a notification was emitted for the tenant
        from Models.notification import Notification
        db = get_session()
        try:
            notifs = db.query(Notification).filter(
                Notification.type == "payment_overdue"
            ).all()
            assert len(notifs) == 1
            assert notifs[0].user_id == seeded_db["tenant"]["user_id"]
        finally:
            db.close()