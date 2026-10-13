
from datetime import datetime
from Database.connection import get_session
from Models.profile_change_request import ProfileChangeRequest


class ProfileChangeRepository:
    def list_all(self):
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .order_by(ProfileChangeRequest.requested_at.desc())
                    .all())
        finally:
            db.close()

    def list_pending(self):
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .filter(ProfileChangeRequest.status == "Pending")
                    .order_by(ProfileChangeRequest.requested_at.desc())
                    .all())
        finally:
            db.close()

    def list_for_user(self, user_id: int):
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .filter(ProfileChangeRequest.user_id == user_id)
                    .order_by(ProfileChangeRequest.requested_at.desc())
                    .all())
        finally:
            db.close()

    def find_by_id(self, request_id: int):
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .filter(ProfileChangeRequest.request_id == request_id)
                    .first())
        finally:
            db.close()

    def find_pending_for_field(self, user_id: int, field_name: str):
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .filter(ProfileChangeRequest.user_id == user_id,
                            ProfileChangeRequest.field_name == field_name,
                            ProfileChangeRequest.status == "Pending")
                    .first())
        finally:
            db.close()

    def create(self, user_id, field_name, old_value, new_value, reason):
        db = get_session()
        try:
            r = ProfileChangeRequest(
                user_id=user_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                status="Pending",
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            return r
        finally:
            db.close()

    def set_status(self, request_id, status, decided_by, decision_note=None):
        db = get_session()
        try:
            r = (db.query(ProfileChangeRequest)
                 .filter(ProfileChangeRequest.request_id == request_id)
                 .first())
            if not r:
                return False
            r.status = status
            r.decided_by = decided_by
            r.decided_at = datetime.utcnow()
            if decision_note is not None:
                r.decision_note = decision_note
            db.commit()
            return True
        finally:
            db.close()

    def pending_count(self) -> int:
        db = get_session()
        try:
            return (db.query(ProfileChangeRequest)
                    .filter(ProfileChangeRequest.status == "Pending")
                    .count())
        finally:
            db.close()
