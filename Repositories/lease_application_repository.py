
from datetime import datetime
from Database.connection import get_session
from Models.lease_application import LeaseApplication


class LeaseApplicationRepository:
    def list_all(self):
        db = get_session()
        try:
            return (
                db.query(LeaseApplication)
                .order_by(LeaseApplication.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def list_for_tenant(self, tenant_id: int):
        db = get_session()
        try:
            return (
                db.query(LeaseApplication)
                .filter(LeaseApplication.tenant_id == tenant_id)
                .order_by(LeaseApplication.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def list_pending_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(LeaseApplication)
                .filter(
                    LeaseApplication.property_id == property_id,
                    LeaseApplication.status == "Pending",
                )
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, application_id: int):
        db = get_session()
        try:
            return db.query(LeaseApplication).filter(
                LeaseApplication.application_id == application_id
            ).first()
        finally:
            db.close()

    def has_pending_for_property(self, property_id: int, tenant_id: int) -> bool:
        db = get_session()
        try:
            return (
                db.query(LeaseApplication)
                .filter(
                    LeaseApplication.property_id == property_id,
                    LeaseApplication.tenant_id == tenant_id,
                    LeaseApplication.status == "Pending",
                )
                .count()
                > 0
            )
        finally:
            db.close()

    def create(self, property_id, tenant_id, preferred_start,
               duration_months, message):
        db = get_session()
        try:
            a = LeaseApplication(
                property_id=property_id,
                tenant_id=tenant_id,
                preferred_start=preferred_start,
                duration_months=duration_months,
                message=message,
                status="Pending",
            )
            db.add(a)
            db.commit()
            db.refresh(a)
            return a
        finally:
            db.close()

    def set_status(self, application_id: int, status: str,
                   decision_note: str | None = None,
                   created_lease_id: int | None = None) -> bool:
        db = get_session()
        try:
            a = db.query(LeaseApplication).filter(
                LeaseApplication.application_id == application_id
            ).first()
            if not a:
                return False
            a.status = status
            if decision_note is not None:
                a.decision_note = decision_note
            if created_lease_id is not None:
                a.created_lease_id = created_lease_id
            if status in ("Approved", "Declined", "Cancelled"):
                a.decided_at = datetime.utcnow()
            db.commit()
            return True
        finally:
            db.close()
