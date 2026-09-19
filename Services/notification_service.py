print(">>> notification_service.py V2 <<<")

from Repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self):
        self.notifications = NotificationRepository()

    # ------------------------------------------------------------------ emit
    def emit(self, user_id, type, title, message, priority="Normal"):
        """
        Persist a notification for a user.
        Called by every other module when an event occurs.
        """
        if not user_id:
            return None
        return self.notifications.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            priority=priority,
        )

    # ------------------------------------------------------------------ reads
    def list_for_user(self, user_id: int):
        rows = self.notifications.list_for_user(user_id)
        return [self._to_dict(n) for n in rows]

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

    # ------------------------------------------------------------------ writes
    def mark_read(self, notification_id: int):
        ok = self.notifications.mark_read(notification_id)
        return (True, "Marked as read.") if ok else (False, "Notification not found.")

    def mark_all_read(self, user_id: int):
        count = self.notifications.mark_all_read(user_id)
        return True, f"{count} notification(s) marked as read."