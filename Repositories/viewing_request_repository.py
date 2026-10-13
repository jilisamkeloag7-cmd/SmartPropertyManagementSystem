
from datetime import datetime
from Database.connection import get_session
from Models.viewing_request import ViewingRequest


class ViewingRequestRepository:
    def list_all(self):
        db = get_session()
        try:
            return (
                db.query(ViewingRequest)
                .order_by(ViewingRequest.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def list_for_tenant(self, tenant_id: int):
        db = get_session()
        try:
            return (
                db.query(ViewingRequest)
                .filter(ViewingRequest.tenant_id == tenant_id)
                .order_by(ViewingRequest.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(ViewingRequest)
                .filter(ViewingRequest.property_id == property_id)
                .order_by(ViewingRequest.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, request_id: int):
        db = get_session()
        try:
            return db.query(ViewingRequest).filter(
                ViewingRequest.request_id == request_id
            ).first()
        finally:
            db.close()

    def has_pending_for_property(self, property_id: int, tenant_id: int) -> bool:
        db = get_session()
        try:
            return (
                db.query(ViewingRequest)
                .filter(
                    ViewingRequest.property_id == property_id,
                    ViewingRequest.tenant_id == tenant_id,
                    ViewingRequest.status == "Pending",
                )
                .count()
                > 0
            )
        finally:
            db.close()

    def create(self, property_id, tenant_id, preferred_date,
               preferred_time, message):
        db = get_session()
        try:
            r = ViewingRequest(
                property_id=property_id,
                tenant_id=tenant_id,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                message=message,
                status="Pending",
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            return r
        finally:
            db.close()

    def set_status(self, request_id: int, status: str,
                   manager_note: str | None = None) -> bool:
        db = get_session()
        try:
            r = db.query(ViewingRequest).filter(
                ViewingRequest.request_id == request_id
            ).first()
            if not r:
                return False
            r.status = status
            if manager_note is not None:
                r.manager_note = manager_note
            if status in ("Approved", "Declined"):
                r.decided_at = datetime.utcnow()
            db.commit()
            return True
        finally:
            db.close()
