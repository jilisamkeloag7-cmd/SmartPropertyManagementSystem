print(">>> notification_repository.py V2 <<<")

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
                .filter(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
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
                .filter(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
                .count()
            )
        finally:
            db.close()

    def find_by_id(self, notification_id: int):
        db = get_session()
        try:
            return (
                db.query(Notification)
                .filter(Notification.notification_id == notification_id)
                .first()
            )
        finally:
            db.close()

    def mark_read(self, notification_id: int) -> bool:
        db = get_session()
        try:
            n = db.query(Notification).filter(
                Notification.notification_id == notification_id
            ).first()
            if not n:
                return False
            if n.read_at is None:
                n.read_at = datetime.utcnow()
                db.commit()
            return True
        finally:
            db.close()

    def mark_all_read(self, user_id: int) -> int:
        db = get_session()
        try:
            rows = (
                db.query(Notification)
                .filter(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
                .all()
            )
            now = datetime.utcnow()
            for n in rows:
                n.read_at = now
            db.commit()
            return len(rows)
        finally:
            db.close()

    def delete_for_user(self, user_id: int) -> int:
        db = get_session()
        try:
            n = db.query(Notification).filter(Notification.user_id == user_id).delete()
            db.commit()
            return n
        finally:
            db.close()