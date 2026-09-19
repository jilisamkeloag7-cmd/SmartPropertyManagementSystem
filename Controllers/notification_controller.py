print(">>> notification_controller.py V1 <<<")

from Services.notification_service import NotificationService
from Services.preference_service import PreferenceService


class NotificationController:
    def __init__(self):
        self.notifications = NotificationService()
        self.preferences = PreferenceService()

    # ------------------------------------------------------------------ reads
    def list_for_user(self, user_id: int):
        return self.notifications.list_for_user(user_id)

    def unread_count(self, user_id: int) -> int:
        return self.notifications.unread_count(user_id)

    def get_preferences(self, user_id: int):
        return self.preferences.list_for_user(user_id)

    # ------------------------------------------------------------------ writes
    def mark_read(self, notification_id: int):
        return self.notifications.mark_read(notification_id)

    def mark_all_read(self, user_id: int):
        return self.notifications.mark_all_read(user_id)

    def set_preference(self, user_id: int, event_type: str, prefs: dict):
        return self.preferences.set(user_id, event_type, prefs)