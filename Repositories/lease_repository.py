print(">>> lease_repository.py V2 <<<")

from datetime import date, timedelta
from Database.connection import get_session
from Models.lease import Lease


class LeaseRepository:
    def list_all(self):
        db = get_session()
        try:
            return db.query(Lease).order_by(Lease.lease_id).all()
        finally:
            db.close()

    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(Lease)
                .filter(Lease.property_id == property_id)
                .order_by(Lease.start_date.desc())
                .all()
            )
        finally:
            db.close()

    def list_for_tenant(self, tenant_id: int):
        db = get_session()
        try:
            return (
                db.query(Lease)
                .filter(Lease.tenant_id == tenant_id)
                .order_by(Lease.start_date.desc())
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, lease_id: int):
        db = get_session()
        try:
            return db.query(Lease).filter(Lease.lease_id == lease_id).first()
        finally:
            db.close()

    def has_active_lease(self, property_id: int) -> bool:
        db = get_session()
        try:
            return (
                db.query(Lease)
                .filter(Lease.property_id == property_id, Lease.status == "Active")
                .count()
                > 0
            )
        finally:
            db.close()

    def find_expiring(self, threshold_days: int = 30):
        db = get_session()
        try:
            today = date.today()
            horizon = today + timedelta(days=threshold_days)
            return (
                db.query(Lease)
                .filter(
                    Lease.status == "Active",
                    Lease.end_date >= today,
                    Lease.end_date <= horizon,
                )
                .all()
            )
        finally:
            db.close()

    def create(self, property_id, tenant_id, start_date, end_date, rent_amount):
        db = get_session()
        try:
            lease = Lease(
                property_id=property_id,
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                rent_amount=rent_amount,
                status="Active",
                termination_requested=False,
                termination_reason=None,
            )
            db.add(lease)
            db.commit()
            db.refresh(lease)
            return lease
        finally:
            db.close()

    def update_status(self, lease_id: int, status: str) -> bool:
        db = get_session()
        try:
            lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
            if not lease:
                return False
            lease.status = status
            db.commit()
            return True
        finally:
            db.close()

    def set_termination_request(self, lease_id: int, requested: bool,
                                 reason: str | None) -> bool:
        db = get_session()
        try:
            lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
            if not lease:
                return False
            lease.termination_requested = requested
            lease.termination_reason = reason
            db.commit()
            return True
        finally:
            db.close()