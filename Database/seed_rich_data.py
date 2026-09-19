print(">>> seed_rich_data.py V1 <<<")

"""
Rich test-data seed script.

WARNING: This script DELETES all existing data in the database
and replaces it with a full test dataset. Run this only on a
development/test environment.

Usage:
    python -m Database.seed_rich_data
"""

from datetime import date, datetime, timedelta
from Database.connection import engine, get_session
from Models.base import Base
import Models  # noqa: F401 — register all models
from Models.user import User, UserRole
from Models.property import Property
from Models.ownership import Ownership
from Models.lease import Lease
from Models.payment import Payment
from Models.maintenance import MaintenanceRequest
from Models.notification import Notification, NotificationPreference
from Services.security import hash_password


def _d(days_offset: int) -> date:
    return date.today() + timedelta(days=days_offset)


def _dt(days_offset: int, hour: int = 9) -> datetime:
    return datetime.utcnow() + timedelta(days=days_offset, hours=hour - datetime.utcnow().hour)


def reset_and_seed():
    # -------- reset
    print("[seed] Dropping and recreating all tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = get_session()
    try:
        # ============================================================
        # USERS
        # ============================================================
        print("[seed] Creating users...")
        admin = User(
            id_number="0000000000", name="System Admin",
            email="admin@spm.local", phone="0000000000",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN, status="Active",
        )
        manager = User(
            id_number="9001015009087", name="Mandy Manager",
            email="manager@spm.local", phone="0812345678",
            password_hash=hash_password("manager123"),
            role=UserRole.MANAGER, status="Active",
        )
        owner1 = User(
            id_number="8505055555080", name="John Owner",
            email="owner@spm.local", phone="0821234567",
            password_hash=hash_password("owner123"),
            role=UserRole.OWNER, status="Active",
        )
        owner2 = User(
            id_number="8807077777080", name="Sarah Landlord",
            email="sarah@spm.local", phone="0827654321",
            password_hash=hash_password("sarah123"),
            role=UserRole.OWNER, status="Active",
        )
        tenant1 = User(
            id_number="0102030405060", name="Jane Tenant",
            email="tenant@spm.local", phone="0837654321",
            password_hash=hash_password("tenant123"),
            role=UserRole.TENANT, status="Active",
        )
        tenant2 = User(
            id_number="0203040506070", name="Thabo Mkhize",
            email="thabo@spm.local", phone="0845555555",
            password_hash=hash_password("thabo123"),
            role=UserRole.TENANT, status="Active",
        )
        tenant3 = User(
            id_number="0304050607080", name="Naledi Zulu",
            email="naledi@spm.local", phone="0856666666",
            password_hash=hash_password("naledi123"),
            role=UserRole.TENANT, status="Active",
        )
        inactive = User(
            id_number="0405060708090", name="Peter Former",
            email="peter@spm.local", phone="0867777777",
            password_hash=hash_password("peter123"),
            role=UserRole.TENANT, status="Inactive",
        )
        db.add_all([admin, manager, owner1, owner2,
                    tenant1, tenant2, tenant3, inactive])
        db.flush()

        # ============================================================
        # PROPERTIES
        # ============================================================
        print("[seed] Creating properties...")
        p1 = Property(
            address="12 Main Rd, Durban", property_type="House",
            build_details="3 bed, 2 bath, built 2010, 250m² yard",
            status="Occupied",
        )
        p2 = Property(
            address="45 Beach Ave, Umhlanga", property_type="Apartment",
            build_details="2 bed, 1 bath, built 2018, sea view",
            status="Occupied",
        )
        p3 = Property(
            address="7 Acacia Close, Pinetown", property_type="House",
            build_details="4 bed, 3 bath, built 2015, double garage",
            status="Occupied",
        )
        p4 = Property(
            address="88 Smith Street, Durban CBD", property_type="Commercial",
            build_details="Shop front, 120m², high foot traffic",
            status="Available",
        )
        p5 = Property(
            address="3 Ridge Road, Kloof", property_type="House",
            build_details="5 bed, 4 bath, built 2020, pool",
            status="Under Maintenance",
        )
        p6 = Property(
            address="21 Umgeni Rd, Springfield", property_type="Apartment",
            build_details="1 bed, 1 bath, built 2021, modern finishes",
            status="Available",
        )
        p7 = Property(
            address="Old Mill Site, Verulam", property_type="Commercial",
            build_details="Warehouse, 800m², decommissioned 2024",
            status="Archived",
        )
        db.add_all([p1, p2, p3, p4, p5, p6, p7])
        db.flush()

        # ============================================================
        # OWNERSHIPS
        # ============================================================
        print("[seed] Creating ownerships...")
        db.add_all([
            Ownership(property_id=p1.property_id, user_id=owner1.user_id,
                      ownership_share=1.0, start_date=_d(-800)),
            Ownership(property_id=p2.property_id, user_id=owner1.user_id,
                      ownership_share=1.0, start_date=_d(-500)),
            Ownership(property_id=p3.property_id, user_id=owner2.user_id,
                      ownership_share=1.0, start_date=_d(-400)),
            Ownership(property_id=p4.property_id, user_id=owner2.user_id,
                      ownership_share=0.6, start_date=_d(-300)),
            Ownership(property_id=p4.property_id, user_id=owner1.user_id,
                      ownership_share=0.4, start_date=_d(-300)),
            Ownership(property_id=p5.property_id, user_id=owner1.user_id,
                      ownership_share=1.0, start_date=_d(-200)),
            Ownership(property_id=p6.property_id, user_id=owner2.user_id,
                      ownership_share=1.0, start_date=_d(-100)),
        ])

        # ============================================================
        # LEASES
        # ============================================================
        print("[seed] Creating leases...")
        # Active lease — well into term
        l1 = Lease(property_id=p1.property_id, tenant_id=tenant1.user_id,
                   start_date=_d(-90), end_date=_d(275),
                   rent_amount=6500.0, status="Active")
        # Active lease — expiring in 20 days (triggers reminder)
        l2 = Lease(property_id=p2.property_id, tenant_id=tenant2.user_id,
                   start_date=_d(-345), end_date=_d(20),
                   rent_amount=8200.0, status="Active")
        # Active lease — expiring in 60 days (no reminder)
        l3 = Lease(property_id=p3.property_id, tenant_id=tenant3.user_id,
                   start_date=_d(-180), end_date=_d(60),
                   rent_amount=11500.0, status="Active")
        # Terminated lease (history)
        l4 = Lease(property_id=p6.property_id, tenant_id=tenant1.user_id,
                   start_date=_d(-400), end_date=_d(-50),
                   rent_amount=4800.0, status="Terminated")
        db.add_all([l1, l2, l3, l4])
        db.flush()

        # ============================================================
        # PAYMENTS — every state
        # ============================================================
        print("[seed] Creating payments...")
        # l1: paid past, paid current month, pending upcoming
        db.add_all([
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(-60), paid_date=_d(-60), status="Paid"),
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(-30), paid_date=_d(-30), status="Paid"),
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(5), paid_date=None, status="Pending"),
        ])
        # l2: overdue, overdue, pending
        db.add_all([
            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(-45), paid_date=_d(-45), status="Paid"),
            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(-15), paid_date=None, status="Overdue"),
            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(15), paid_date=None, status="Pending"),
        ])
        # l3: paid, paid, pending
        db.add_all([
            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(-90), paid_date=_d(-90), status="Paid"),
            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(-60), paid_date=_d(-62), status="Paid"),
            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(3), paid_date=None, status="Pending"),
        ])
        # l4: historical
        db.add_all([
            Payment(lease_id=l4.lease_id, amount=4800.0,
                    due_date=_d(-200), paid_date=_d(-200), status="Paid"),
            Payment(lease_id=l4.lease_id, amount=4800.0,
                    due_date=_d(-150), paid_date=_d(-148), status="Paid"),
        ])

        # ============================================================
        # MAINTENANCE — all states
        # ============================================================
        print("[seed] Creating maintenance requests...")
        db.add_all([
            MaintenanceRequest(
                property_id=p1.property_id, submitted_by=tenant1.user_id,
                description="Kitchen tap leaking continuously. Bucket needed overnight.",
                priority="Medium", status="Open",
                created_at=_dt(-2),
            ),
            MaintenanceRequest(
                property_id=p2.property_id, submitted_by=tenant2.user_id,
                description="Geyser burst on Saturday. No hot water.",
                priority="Urgent", status="In Progress",
                created_at=_dt(-5),
            ),
            MaintenanceRequest(
                property_id=p3.property_id, submitted_by=tenant3.user_id,
                description="Garage door motor making grinding noise.",
                priority="Low", status="Resolved",
                created_at=_dt(-30),
            ),
            MaintenanceRequest(
                property_id=p3.property_id, submitted_by=tenant3.user_id,
                description="Bedroom window cracked after storm.",
                priority="High", status="Closed",
                created_at=_dt(-60), completed_at=_dt(-50),
            ),
            MaintenanceRequest(
                property_id=p5.property_id, submitted_by=owner1.user_id,
                description="Pool pump needs replacing before tenant can move in.",
                priority="High", status="In Progress",
                created_at=_dt(-10),
            ),
        ])

        # ============================================================
        # NOTIFICATIONS
        # ============================================================
        print("[seed] Creating notifications...")
        db.add_all([
            # Jane (tenant1)
            Notification(user_id=tenant1.user_id, type="payment_due",
                         title="Rent due in 5 days",
                         message="Your rent of R6500.00 is due on "
                                 f"{_d(5).isoformat()}.",
                         priority="Normal", created_at=_dt(-1), read_at=None),
            Notification(user_id=tenant1.user_id, type="maintenance_update",
                         title="Request #1 received",
                         message="Your maintenance request has been logged.",
                         priority="Normal", created_at=_dt(-2),
                         read_at=_dt(-2, hour=10)),
            # Thabo (tenant2) — overdue + lease expiring
            Notification(user_id=tenant2.user_id, type="payment_overdue",
                         title="Payment overdue",
                         message="Payment of R8200.00 was due 15 days ago.",
                         priority="High", created_at=_dt(-1), read_at=None),
            Notification(user_id=tenant2.user_id, type="lease_expiring",
                         title="Lease expiring soon",
                         message="Your lease expires in 20 days.",
                         priority="High", created_at=_dt(-1), read_at=None),
            # Naledi (tenant3)
            Notification(user_id=tenant3.user_id, type="payment_due",
                         title="Rent due in 3 days",
                         message="Your rent of R11500.00 is due soon.",
                         priority="Normal", created_at=_dt(0), read_at=None),
            # Manager
            Notification(user_id=manager.user_id, type="maintenance_new",
                         title="Urgent request — Geyser burst",
                         message="Property #2 has an Urgent request.",
                         priority="High", created_at=_dt(-5), read_at=None),
        ])

        # ============================================================
        # NOTIFICATION PREFERENCES (defaults for each user)
        # ============================================================
        print("[seed] Creating notification preferences...")
        for u in [admin, manager, owner1, owner2, tenant1, tenant2, tenant3]:
            for event in ["payment_due", "payment_overdue",
                          "lease_expiring", "maintenance_new", "maintenance_update"]:
                db.add(NotificationPreference(
                    user_id=u.user_id, event_type=event,
                    dashboard_enabled=True,
                    email_enabled=(event != "maintenance_new"),
                    timing={"payment_due": 3, "payment_overdue": 1,
                            "lease_expiring": 30}.get(event, 0),
                ))

        db.commit()
        print("[seed] ✅ Rich test data created successfully.")
        print()
        print("=" * 60)
        print("TEST ACCOUNTS")
        print("=" * 60)
        print(f"{'Role':<20} {'Email':<25} {'Password'}")
        print("-" * 60)
        print(f"{'Administrator':<20} admin@spm.local          admin123")
        print(f"{'Property Manager':<20} manager@spm.local        manager123")
        print(f"{'Owner (John)':<20} owner@spm.local          owner123")
        print(f"{'Owner (Sarah)':<20} sarah@spm.local          sarah123")
        print(f"{'Tenant (Jane)':<20} tenant@spm.local         tenant123")
        print(f"{'Tenant (Thabo)':<20} thabo@spm.local          thabo123")
        print(f"{'Tenant (Naledi)':<20} naledi@spm.local         naledi123")
        print(f"{'Inactive (Peter)':<20} peter@spm.local          peter123")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed()