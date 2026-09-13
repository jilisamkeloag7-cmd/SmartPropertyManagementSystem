"""Creates all tables and seeds demo data (idempotent)."""
from datetime import date, timedelta
from Database.connection import engine, get_session
from Models.base import Base
import Models  # noqa: F401 — ensures all models register
from Models.user import User, UserRole
from Models.property import Property
from Models.ownership import Ownership
from Models.lease import Lease
from Models.payment import Payment
from Models.maintenance import MaintenanceRequest
from Services.security import hash_password   # ← NEW: real bcrypt hashing


def create_tables():
    Base.metadata.create_all(engine)
    print("[DB] Tables created / verified.")


def seed_demo_data():
    db = get_session()
    try:
        if db.query(User).count() > 0:
            print("[DB] Data already present — skipping seed.")
            return

        admin = User(
            id_number="0000000000", name="System Admin",
            email="admin@spm.local", phone="0000000000",
            password_hash=hash_password("admin123"),   # ← hashed
            role=UserRole.ADMIN
        )
        owner = User(
            id_number="9001015009087", name="John Owner",
            email="owner@spm.local", phone="0821234567",
            password_hash=hash_password("owner123"),   # ← hashed
            role=UserRole.OWNER
        )
        tenant = User(
            id_number="0102030405060", name="Jane Tenant",
            email="tenant@spm.local", phone="0837654321",
            password_hash=hash_password("tenant123"),  # ← hashed
            role=UserRole.TENANT
        )
        db.add_all([admin, owner, tenant]); db.flush()

        p1 = Property(address="12 Main Rd, Durban", property_type="House",
                      build_details="3 bed, 2 bath, built 2010", status="Occupied")
        p2 = Property(address="45 Beach Ave, Umhlanga", property_type="Apartment",
                      build_details="2 bed, 1 bath, built 2018", status="Occupied")
        db.add_all([p1, p2]); db.flush()

        db.add_all([
            Ownership(property_id=p1.property_id, user_id=owner.user_id,
                      ownership_share=1.0, start_date=date(2020, 1, 1)),
            Ownership(property_id=p2.property_id, user_id=owner.user_id,
                      ownership_share=1.0, start_date=date(2021, 6, 1)),
        ])

        lease = Lease(property_id=p1.property_id, tenant_id=tenant.user_id,
                      start_date=date.today() - timedelta(days=90),
                      end_date=date.today() + timedelta(days=275),
                      rent_amount=6500.0, status="Active")
        db.add(lease); db.flush()

        db.add(Payment(lease_id=lease.lease_id, amount=6500.0,
                       due_date=date.today() + timedelta(days=5), status="Pending"))

        db.add(MaintenanceRequest(property_id=p1.property_id, submitted_by=tenant.user_id,
                                  description="Leaking kitchen tap", priority="Medium",
                                  status="Open"))

        db.commit()
        print("[DB] Demo data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_demo_data()