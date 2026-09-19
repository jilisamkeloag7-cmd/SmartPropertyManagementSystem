print(">>> notification_repository.py V1 <<<")

from datetime import datetime
from Database.connection import get_session
from Models.notification import Notification


class NotificationRepository:
    def create(self, user_id, type, title, message, priority="Normal"):
        db = get_session()
        try:
            n = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                priority=priority,
                created_at=datetime.utcnow(),
                read_at=None,
            )
            db.add(n)
            db.commit()
            db.refresh(n)
            return n
        finally:
            db.close()

    def list_for_user(self, user_id: int):
        db = get_session()
        try:
            return (
                db.query(Notification)
                .filter(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def list_unread(self, user_id: int):
        db = get_session()
        try:
            return (
                db.query(Notification)
                .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
                .order_by(Notification.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def count_unread(self, user_id: int) -> int:
        db = get_session()
        try:
            return (
                db.query(Notification)
                .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
                .count()
            )
        finally:
            db.close()

    def mark_read(self, notification_id: int) -> bool:
        db = get_session()
        try:
            n = db.query(Notification).filter(Notification.notification_id == notification_id).first()
            if not n:
                return False
            n.read_at = datetime.utcnow()
            db.commit()
            return True
        finally:
            db.close()