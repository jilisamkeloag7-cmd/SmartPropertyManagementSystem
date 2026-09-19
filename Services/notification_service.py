print(">>> notification_service.py V1 <<<")

from Repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self):
        self.notifications = NotificationRepository()

    def emit(self, user_id, type, title, message, priority="Normal"):
        """
        Persist a notification for a user.
        (Email queue wiring happens in Module 9 / Module 10.)
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