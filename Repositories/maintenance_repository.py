
from datetime import datetime
from Database.connection import get_session
from Models.maintenance import MaintenanceRequest


class MaintenanceRepository:
    def list_all(self):
        db = get_session()
        try:
            return db.query(MaintenanceRequest).order_by(
                MaintenanceRequest.request_id.desc()
            ).all()
        finally:
            db.close()

    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(MaintenanceRequest.property_id == property_id)
                .order_by(MaintenanceRequest.request_id.desc())
                .all()
            )
        finally:
            db.close()

    def list_for_submitter(self, user_id: int):
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(MaintenanceRequest.submitted_by == user_id)
                .order_by(MaintenanceRequest.request_id.desc())
                .all()
            )
        finally:
            db.close()

    def list_open(self):
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(MaintenanceRequest.status.in_(["Open", "In Progress"]))
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, request_id: int):
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(MaintenanceRequest.request_id == request_id)
                .first()
            )
        finally:
            db.close()

    def has_open_request(self, property_id: int) -> bool:
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(
                    MaintenanceRequest.property_id == property_id,
                    MaintenanceRequest.status.in_(["Open", "In Progress"]),
                )
                .count()
                > 0
            )
        finally:
            db.close()

    def create(self, property_id, submitted_by, description,
               priority="Medium", status="Open"):
        db = get_session()
        try:
            req = MaintenanceRequest(
                property_id=property_id,
                submitted_by=submitted_by,
                description=description,
                priority=priority,
                status=status,
                created_at=datetime.utcnow(),
            )
            db.add(req)
            db.commit()
            db.refresh(req)
            return req
        finally:
            db.close()

    def update_status(self, request_id: int, status: str, completed_at=None):
        db = get_session()
        try:
            req = db.query(MaintenanceRequest).filter(
                MaintenanceRequest.request_id == request_id
            ).first()
            if not req:
                return False
            req.status = status
            req.completed_at = completed_at
            db.commit()
            return True
        finally:
            db.close()
