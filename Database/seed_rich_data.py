print(">>> seed_rich_data.py V9 <<<")

"""
Rich test-data seed script.

WARNING: This script DELETES all data in the database.
Run only on development/test environments.

The script PRESERVES existing property_image links across reseeds:
before dropping tables, it snapshots the property_images rows, and
after recreating the schema, it restores those rows for any file that
still exists on disk.

Usage:
    python -m Database.seed_rich_data
"""

import os
import re
from Services.security import hash_answer
from Models.viewing_request import ViewingRequest
from Models.lease_application import LeaseApplication
from datetime import date, datetime, timedelta
from Database.connection import engine, get_session
from Models.base import Base
import Models  # noqa: F401
from Models.user import User, UserRole
from Models.property import Property
from Models.property_image import PropertyImage
from Models.ownership import Ownership
from Models.lease import Lease
from Models.payment import Payment
from Models.maintenance import MaintenanceRequest
from Models.notification import Notification, NotificationPreference
from Models.review import Review
from Services.security import hash_password
from Services.property_image_service import IMAGES_DIR


def _d(days_offset: int) -> date:
    return date.today() + timedelta(days=days_offset)


def _dt(days_offset: int, hour: int = 9) -> datetime:
    return datetime.utcnow() + timedelta(days=days_offset,
                                          hours=hour - datetime.utcnow().hour)


# =====================================================================
# IMAGE PRESERVATION HELPERS
# =====================================================================

def _snapshot_image_links():
    """Read all current image links before the DB is wiped."""
    db = get_session()
    try:
        rows = db.query(PropertyImage).all()
        return [
            (r.property_id, r.filename, r.order_index)
            for r in rows
        ]
    except Exception as e:
        # Table doesn't exist yet (first ever run) → nothing to preserve
        print(f"[seed] No image snapshot (reason: {type(e).__name__}).")
        return []
    finally:
        db.close()


def _restore_image_links(db, snapshot, valid_property_ids: set) -> int:
    """Re-insert image links captured before the drop. Files must exist on disk."""
    restored = 0
    for property_id, filename, order_index in snapshot:
        if property_id not in valid_property_ids:
            continue
        full_path = os.path.join(IMAGES_DIR, filename)
        if not os.path.isfile(full_path):
            continue
        db.add(PropertyImage(
            property_id=property_id,
            filename=filename,
            order_index=order_index,
        ))
        restored += 1
    return restored


def _auto_link_new_files(db, valid_property_ids: set,
                          already_linked: set) -> int:
    """
    Scan Assets/property_images/ for p{ID}_*.{ext} files not already
    linked in the restored snapshot, and link them.

    This handles images uploaded after a property was created but
    before a seed run.
    """
    if not os.path.isdir(IMAGES_DIR):
        return 0

    pattern = re.compile(r"^p(\d+)_")
    image_counts = {}
    linked = 0

    for filename in sorted(os.listdir(IMAGES_DIR)):
        if filename == ".gitkeep" or not os.path.isfile(os.path.join(IMAGES_DIR, filename)):
            continue
        if filename in already_linked:
            continue

        m = pattern.match(filename)
        if not m:
            continue

        try:
            prop_id = int(m.group(1))
        except ValueError:
            continue

        if prop_id not in valid_property_ids:
            continue

        order = image_counts.get(prop_id, 0)
        image_counts[prop_id] = order + 1

        db.add(PropertyImage(
            property_id=prop_id,
            filename=filename,
            order_index=order,
        ))
        linked += 1

    return linked


# =====================================================================
# MAIN SEED
# =====================================================================

def reset_and_seed():
    # ---- 1. Snapshot image links BEFORE dropping tables
    print("[seed] Snapshotting existing image links...")
    image_snapshot = _snapshot_image_links()
    print(f"[seed] {len(image_snapshot)} image link(s) snapshotted.")

    print("[seed] Dropping and recreating all tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = get_session()
    try:
        # ============================================================
        # USERS
        # ============================================================
        print("[seed] Creating users...")

        SEC_Q = "What is your mother's maiden name?"

        admin = User(id_number="0000000000", name="System Admin",
                     email="admin@spm.local", phone="0000000000",
                     password_hash=hash_password("admin123"),
                     role=UserRole.ADMIN, status="Active",
                     security_question=SEC_Q, security_answer_hash=hash_answer("root"))
        manager = User(id_number="9001015009087", name="Mandy Manager",
                       email="manager@spm.local", phone="0812345678",
                       password_hash=hash_password("manager123"),
                       role=UserRole.MANAGER, status="Active",
                       security_question=SEC_Q, security_answer_hash=hash_answer("mandy"))
        owner1 = User(id_number="8505055555080", name="John Owner",
                      email="owner@spm.local", phone="0821234567",
                      password_hash=hash_password("owner123"),
                      role=UserRole.OWNER, status="Active",
                      security_question=SEC_Q, security_answer_hash=hash_answer("john"))
        owner2 = User(id_number="8807077777080", name="Sarah Landlord",
                      email="sarah@spm.local", phone="0827654321",
                      password_hash=hash_password("sarah123"),
                      role=UserRole.OWNER, status="Active",
                      security_question=SEC_Q, security_answer_hash=hash_answer("sarah"))
        tenant1 = User(id_number="0102030405060", name="Jane Tenant",
                       email="tenant@spm.local", phone="0837654321",
                       password_hash=hash_password("tenant123"),
                       role=UserRole.TENANT, status="Active",
                       security_question=SEC_Q, security_answer_hash=hash_answer("jane"))
        tenant2 = User(id_number="0203040506070", name="Thabo Mkhize",
                       email="thabo@spm.local", phone="0845555555",
                       password_hash=hash_password("thabo123"),
                       role=UserRole.TENANT, status="Active",
                       security_question=SEC_Q, security_answer_hash=hash_answer("thabo"))
        tenant3 = User(id_number="0304050607080", name="Naledi Zulu",
                       email="naledi@spm.local", phone="0856666666",
                       password_hash=hash_password("naledi123"),
                       role=UserRole.TENANT, status="Active",
                       security_question=SEC_Q, security_answer_hash=hash_answer("naledi"))
        inactive = User(id_number="0405060708090", name="Peter Former",
                        email="peter@spm.local", phone="0867777777",
                        password_hash=hash_password("peter123"),
                        role=UserRole.TENANT, status="Inactive",
                        security_question=SEC_Q, security_answer_hash=hash_answer("peter"))
        db.add_all([admin, manager, owner1, owner2,
                    tenant1, tenant2, tenant3, inactive])
        db.flush()

        print()
        print("Security Q for all test accounts: 'What is your mother's maiden name?'")
        print("Answers: root, mandy, john, sarah, jane, thabo, naledi, peter")
        print("(each matches the respective user, lowercase)")

        # ============================================================
        # PROPERTIES
        # ============================================================
        print("[seed] Creating properties...")
        p1 = Property(address="12 Main Rd, Durban", property_type="House",
                      build_details="3 bed, 2 bath, built 2010, 250m² yard",
                      status="Occupied", listing_price=6500.0)
        p2 = Property(address="45 Beach Ave, Umhlanga", property_type="Apartment",
                      build_details="2 bed, 1 bath, built 2018, sea view",
                      status="Occupied", listing_price=8200.0)
        p3 = Property(address="7 Acacia Close, Pinetown", property_type="House",
                      build_details="4 bed, 3 bath, built 2015, double garage",
                      status="Occupied", listing_price=11500.0)
        p4 = Property(address="88 Smith Street, Durban CBD", property_type="Commercial",
                      build_details="Shop front, 120m², high foot traffic",
                      status="Available", listing_price=14000.0)
        p5 = Property(address="3 Ridge Road, Kloof", property_type="House",
                      build_details="5 bed, 4 bath, built 2020, pool",
                      status="Under Maintenance", listing_price=18500.0)
        p6 = Property(address="21 Umgeni Rd, Springfield", property_type="Apartment",
                      build_details="1 bed, 1 bath, built 2021, modern finishes",
                      status="Available", listing_price=4800.0)
        p7 = Property(address="Old Mill Site, Verulam", property_type="Commercial",
                      build_details="Warehouse, 800m², decommissioned 2024",
                      status="Archived", listing_price=None)
        db.add_all([p1, p2, p3, p4, p5, p6, p7])
        db.flush()

        # ============================================================
        # IMAGES — restore snapshot + auto-link new files
        # ============================================================
        print("[seed] Restoring property image links...")
        valid_ids = {p1.property_id, p2.property_id, p3.property_id,
                     p4.property_id, p5.property_id, p6.property_id,
                     p7.property_id}

        restored = _restore_image_links(db, image_snapshot, valid_ids)
        print(f"[seed] {restored} image link(s) restored from previous session.")

        # Auto-link newly added files that weren't in the snapshot
        already_linked = {fn for _, fn, _ in image_snapshot}
        auto_linked = _auto_link_new_files(db, valid_ids, already_linked)
        if auto_linked:
            print(f"[seed] {auto_linked} new image file(s) auto-linked.")

        if restored == 0 and auto_linked == 0:
            print("[seed] No images to link (that's fine — cards will show placeholders).")

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
        l1 = Lease(property_id=p1.property_id, tenant_id=tenant1.user_id,
                   start_date=_d(-90), end_date=_d(275),
                   rent_amount=6500.0, status="Active")
        l2 = Lease(property_id=p2.property_id, tenant_id=tenant2.user_id,
                   start_date=_d(-345), end_date=_d(20),
                   rent_amount=8200.0, status="Active")
        l3 = Lease(property_id=p3.property_id, tenant_id=tenant3.user_id,
                   start_date=_d(-180), end_date=_d(60),
                   rent_amount=11500.0, status="Active")
        l4 = Lease(property_id=p6.property_id, tenant_id=tenant1.user_id,
                   start_date=_d(-400), end_date=_d(-100),
                   rent_amount=4800.0, status="Terminated")
        l5 = Lease(property_id=p6.property_id, tenant_id=tenant3.user_id,
                   start_date=_d(-90), end_date=_d(-30),
                   rent_amount=4800.0, status="Terminated")
        l6 = Lease(property_id=p4.property_id, tenant_id=tenant2.user_id,
                   start_date=_d(-600), end_date=_d(-400),
                   rent_amount=14000.0, status="Terminated")
        l7 = Lease(property_id=p5.property_id, tenant_id=tenant3.user_id,
                   start_date=_d(-500), end_date=_d(-300),
                   rent_amount=18500.0, status="Terminated")
        l8 = Lease(property_id=p1.property_id, tenant_id=tenant3.user_id,
                   start_date=_d(-900), end_date=_d(-700),
                   rent_amount=6500.0, status="Terminated")
        l9 = Lease(property_id=p3.property_id, tenant_id=tenant1.user_id,
                   start_date=_d(-800), end_date=_d(-600),
                   rent_amount=11500.0, status="Terminated")
        db.add_all([l1, l2, l3, l4, l5, l6, l7, l8, l9])
        db.flush()

        # ============================================================
        # PAYMENTS
        # ============================================================
        print("[seed] Creating payments...")
        db.add_all([
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(-60), paid_date=_d(-60), status="Paid"),
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(-30), paid_date=_d(-30), status="Paid"),
            Payment(lease_id=l1.lease_id, amount=6500.0,
                    due_date=_d(5), paid_date=None, status="Pending"),

            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(-45), paid_date=_d(-45), status="Paid"),
            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(-15), paid_date=None, status="Overdue"),
            Payment(lease_id=l2.lease_id, amount=8200.0,
                    due_date=_d(15), paid_date=None, status="Pending"),

            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(-90), paid_date=_d(-90), status="Paid"),
            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(-60), paid_date=_d(-62), status="Paid"),
            Payment(lease_id=l3.lease_id, amount=11500.0,
                    due_date=_d(3), paid_date=None,
                    status="Awaiting Confirmation",
                    tenant_marked_at=_dt(-1),
                    payment_reference="EFT-2026-09-21-A17X — paid via capitec app"),

            Payment(lease_id=l4.lease_id, amount=4800.0,
                    due_date=_d(-200), paid_date=_d(-200), status="Paid"),
            Payment(lease_id=l4.lease_id, amount=4800.0,
                    due_date=_d(-150), paid_date=_d(-148), status="Paid"),
        ])

        # ============================================================
        # MAINTENANCE
        # ============================================================
        print("[seed] Creating maintenance requests...")
        db.add_all([
            MaintenanceRequest(property_id=p1.property_id,
                               submitted_by=tenant1.user_id,
                               description="Kitchen tap leaking continuously. Bucket needed overnight.",
                               priority="Medium", status="Open", created_at=_dt(-2)),
            MaintenanceRequest(property_id=p2.property_id,
                               submitted_by=tenant2.user_id,
                               description="Geyser burst on Saturday. No hot water.",
                               priority="Urgent", status="In Progress", created_at=_dt(-5)),
            MaintenanceRequest(property_id=p3.property_id,
                               submitted_by=tenant3.user_id,
                               description="Garage door motor making grinding noise.",
                               priority="Low", status="Resolved", created_at=_dt(-30)),
            MaintenanceRequest(property_id=p3.property_id,
                               submitted_by=tenant3.user_id,
                               description="Bedroom window cracked after storm.",
                               priority="High", status="Closed",
                               created_at=_dt(-60), completed_at=_dt(-50)),
            MaintenanceRequest(property_id=p5.property_id,
                               submitted_by=owner1.user_id,
                               description="Pool pump needs replacing before tenant can move in.",
                               priority="High", status="In Progress", created_at=_dt(-10)),
        ])

        # ============================================================
        # VIEWING REQUESTS
        # ============================================================
        print("[seed] Creating viewing requests...")
        db.add_all([
            # Pending — waiting for manager decision
            ViewingRequest(property_id=p4.property_id, tenant_id=tenant1.user_id,
                           preferred_date=_d(3), preferred_time="Morning",
                           message="Interested in the shop front — available to view "
                                   "any morning this week.",
                           status="Pending", created_at=_dt(-1)),
            ViewingRequest(property_id=p6.property_id, tenant_id=tenant2.user_id,
                           preferred_date=_d(2), preferred_time="Afternoon",
                           message="Please confirm if the apartment is pet-friendly.",
                           status="Pending", created_at=_dt(-1, hour=15)),

            # Approved — historical
            ViewingRequest(property_id=p1.property_id, tenant_id=tenant1.user_id,
                           preferred_date=_d(-60), preferred_time="Morning",
                           message="Would like to view before signing.",
                           status="Approved",
                           manager_note="Confirmed for 9am. Agent will meet you at the gate.",
                           created_at=_dt(-62), decided_at=_dt(-61)),

            # Declined — historical
            ViewingRequest(property_id=p2.property_id, tenant_id=tenant3.user_id,
                           preferred_date=_d(-30), preferred_time="Evening",
                           message="Can I view after work hours?",
                           status="Declined",
                           manager_note="Property is currently occupied. Please choose a daytime slot.",
                           created_at=_dt(-32), decided_at=_dt(-31)),

            # Cancelled by tenant — historical
            ViewingRequest(property_id=p4.property_id, tenant_id=tenant3.user_id,
                           preferred_date=_d(-15), preferred_time="Morning",
                           message="Tentatively interested.",
                           status="Cancelled",
                           created_at=_dt(-18), decided_at=_dt(-17)),
        ])

        # ============================================================
        # NOTIFICATIONS
        # ============================================================
        print("[seed] Creating notifications...")
        db.add_all([
            Notification(user_id=tenant1.user_id, type="payment_due",
                         title="Rent due in 5 days",
                         message=f"Your rent of R6500.00 is due on {_d(5).isoformat()}.",
                         priority="Normal", created_at=_dt(-1), read_at=None),
            Notification(user_id=tenant1.user_id, type="maintenance_update",
                         title="Request #1 received",
                         message="Your maintenance request has been logged.",
                         priority="Normal", created_at=_dt(-2), read_at=_dt(-2, hour=10)),
            Notification(user_id=tenant2.user_id, type="payment_overdue",
                         title="Payment overdue",
                         message="Payment of R8200.00 was due 15 days ago.",
                         priority="High", created_at=_dt(-1), read_at=None),
            Notification(user_id=tenant2.user_id, type="lease_expiring",
                         title="Lease expiring soon",
                         message="Your lease expires in 20 days.",
                         priority="High", created_at=_dt(-1), read_at=None),
            Notification(user_id=tenant3.user_id, type="payment_due",
                         title="Rent due in 3 days",
                         message="Your rent of R11500.00 is due soon.",
                         priority="Normal", created_at=_dt(0), read_at=None),
            Notification(user_id=manager.user_id, type="maintenance_new",
                         title="Urgent request — Geyser burst",
                         message="Property #2 has an Urgent request.",
                         priority="High", created_at=_dt(-5), read_at=None),
        ])

        # ============================================================
        # LEASE APPLICATIONS
        # ============================================================
        print("[seed] Creating lease applications...")
        db.add_all([
            # Pending — waiting for manager decision
            LeaseApplication(property_id=p6.property_id, tenant_id=tenant1.user_id,
                             preferred_start=_d(14), duration_months=12,
                             message="I'm interested in the Springfield apartment. "
                                     "Looking for a 12-month lease starting mid-October.",
                             status="Pending", created_at=_dt(-1)),
            LeaseApplication(property_id=p4.property_id, tenant_id=tenant2.user_id,
                             preferred_start=_d(30), duration_months=24,
                             message="Interested in the shop front for a small business. "
                                     "Planning to sign a 2-year lease.",
                             status="Pending", created_at=_dt(-2)),

            # Approved — reference to historical lease
            LeaseApplication(property_id=p1.property_id, tenant_id=tenant1.user_id,
                             preferred_start=_d(-90), duration_months=12,
                             message="Family home — matches our needs perfectly.",
                             status="Approved",
                             decision_note="Approved. Welcome to 12 Main Rd!",
                             created_lease_id=l1.lease_id,
                             created_at=_dt(-95), decided_at=_dt(-92)),

            # Declined — historical
            LeaseApplication(property_id=p2.property_id, tenant_id=tenant3.user_id,
                             preferred_start=_d(-400), duration_months=6,
                             message="Interested in a short-term lease.",
                             status="Declined",
                             decision_note="Property already occupied by another tenant.",
                             created_at=_dt(-405), decided_at=_dt(-403)),

            # Cancelled by tenant
            LeaseApplication(property_id=p4.property_id, tenant_id=tenant3.user_id,
                             preferred_start=_d(-30), duration_months=12,
                             message="Tentatively exploring options.",
                             status="Cancelled",
                             decision_note="Withdrawn by tenant.",
                             created_at=_dt(-35), decided_at=_dt(-33)),
        ])

        # ============================================================
        # NOTIFICATION PREFERENCES
        # ============================================================
        print("[seed] Creating notification preferences...")
        for u in [admin, manager, owner1, owner2, tenant1, tenant2, tenant3]:
            for event in ["payment_due", "payment_overdue", "lease_expiring",
                          "maintenance_new", "maintenance_update"]:
                db.add(NotificationPreference(
                    user_id=u.user_id, event_type=event,
                    dashboard_enabled=True,
                    email_enabled=(event != "maintenance_new"),
                    timing={"payment_due": 3, "payment_overdue": 1,
                            "lease_expiring": 30}.get(event, 0),
                ))

        # ============================================================
        # REVIEWS
        # ============================================================
        print("[seed] Creating reviews...")
        reviews = [
            Review(property_id=p1.property_id, reviewer_id=tenant1.user_id,
                   rating=4,
                   comment=("Great location, walking distance to shops. "
                            "Water pressure in the main bathroom was an issue "
                            "but the landlord responded quickly."),
                   created_at=_dt(-60)),
            Review(property_id=p3.property_id, reviewer_id=tenant1.user_id,
                   rating=5,
                   comment=("Beautiful family home with plenty of space. "
                            "Loved the double garage. Would definitely rent again."),
                   created_at=_dt(-550)),
            Review(property_id=p6.property_id, reviewer_id=tenant1.user_id,
                   rating=3,
                   comment=("Cozy apartment, good value for the price. "
                            "A bit small for two people but fine for one."),
                   created_at=_dt(-150)),

            Review(property_id=p2.property_id, reviewer_id=tenant2.user_id,
                   rating=5,
                   comment=("Stunning sea views — waking up to the ocean was "
                            "incredible. Can get noisy on weekends."),
                   created_at=_dt(-200)),
            Review(property_id=p4.property_id, reviewer_id=tenant2.user_id,
                   rating=3,
                   comment=("Decent commercial space with high foot traffic. "
                            "Parking was tight during peak hours."),
                   created_at=_dt(-450)),

            Review(property_id=p1.property_id, reviewer_id=tenant3.user_id,
                   rating=4,
                   comment=("Comfortable home in a quiet neighbourhood. "
                            "Friendly neighbours and safe area."),
                   created_at=_dt(-750)),
            Review(property_id=p3.property_id, reviewer_id=tenant3.user_id,
                   rating=5,
                   comment=("Spacious family home. The double garage was a "
                            "lifesaver with two cars. Highly recommend."),
                   created_at=_dt(-120)),
            Review(property_id=p5.property_id, reviewer_id=tenant3.user_id,
                   rating=2,
                   comment=("Pool needed significant work when we moved in. "
                            "Took months to get it functional. House itself "
                            "was fine but the maintenance was slow."),
                   created_at=_dt(-380)),
            Review(property_id=p6.property_id, reviewer_id=tenant3.user_id,
                   rating=4,
                   comment=("Modern finishes and safe area. Would recommend "
                            "for young professionals."),
                   created_at=_dt(-40)),
        ]
        db.add_all(reviews)

        db.commit()
        print("[seed] ✅ Rich test data created successfully.")
        print(f"[seed] {len(reviews)} reviews created across all active properties.")
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