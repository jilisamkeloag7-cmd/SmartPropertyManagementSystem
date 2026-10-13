
from Repositories.notification_repository import NotificationRepository
from Services.email_service import EmailService


class NotificationService:
    def __init__(self):
        self.notifications = NotificationRepository()
        self.email_service = EmailService()

    def emit(self, user_id, type, title, message, priority="Normal"):
        if not user_id:
            return None

        # 1. Persist
        n = self.notifications.create(
            user_id=user_id, type=type, title=title,
            message=message, priority=priority,
        )

        # 2. Fire email (async, skips fake addresses)
        try:
            self.email_service.queue(n)
        except Exception as e:
            print(f"[notification] email dispatch failed: {e}")

        return n

    # ------------------------------------------------------------------ reads
    def list_for_user(self, user_id: int):
        return [self._to_dict(n) for n in self.notifications.list_for_user(user_id)]

    def unread_count(self, user_id: int) -> int:
        return self.notifications.count_unread(user_id)

    @staticmethod
    def _to_dict(n):
        return {
            "notification_id": n.notification_id,
            "user_id": n.user_id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "priority": n.priority,
            "created_at": n.created_at,
            "read_at": n.read_at,
            "is_unread": n.read_at is None,
        }

    def mark_read(self, notification_id: int):
        ok = self.notifications.mark_read(notification_id)
        return (True, "Marked as read.") if ok else (False, "Notification not found.")

    def mark_all_read(self, user_id: int):
        count = self.notifications.mark_all_read(user_id)
        return True, f"{count} notification(s) marked as read."
