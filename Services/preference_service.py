
from Database.connection import get_session
from Models.notification import NotificationPreference


# Supported event types and their defaults
EVENT_TYPES = [
    "payment_due",
    "payment_overdue",
    "lease_expiring",
    "maintenance_new",
    "maintenance_update",
]

DEFAULT_PREFERENCES = {
    "payment_due":        {"dashboard_enabled": True, "email_enabled": True,  "timing": 3},
    "payment_overdue":    {"dashboard_enabled": True, "email_enabled": True,  "timing": 1},
    "lease_expiring":     {"dashboard_enabled": True, "email_enabled": True,  "timing": 30},
    "maintenance_new":    {"dashboard_enabled": True, "email_enabled": False, "timing": 0},
    "maintenance_update": {"dashboard_enabled": True, "email_enabled": False, "timing": 0},
}


class PreferenceService:
    def __init__(self):
        pass

    # ------------------------------------------------------------------ reads
    def get(self, user_id: int, event_type: str) -> dict:
        """Returns a dict for the preference; falls back to defaults if no row."""
        db = get_session()
        try:
            row = (
                db.query(NotificationPreference)
                .filter(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.event_type == event_type,
                )
                .first()
            )
            if row:
                return {
                    "preference_id": row.preference_id,
                    "dashboard_enabled": row.dashboard_enabled,
                    "email_enabled": row.email_enabled,
                    "timing": row.timing,
                }
            defaults = DEFAULT_PREFERENCES.get(
                event_type, {"dashboard_enabled": True, "email_enabled": True, "timing": 0}
            )
            return {
                "preference_id": None,
                "dashboard_enabled": defaults["dashboard_enabled"],
                "email_enabled": defaults["email_enabled"],
                "timing": defaults["timing"],
            }
        finally:
            db.close()

    def list_for_user(self, user_id: int) -> list[dict]:
        """Returns one entry per supported event type, with defaults filled in."""
        out = []
        for event in EVENT_TYPES:
            pref = self.get(user_id, event)
            pref["event_type"] = event
            out.append(pref)
        return out

    def should_email(self, user_id: int, event_type: str) -> bool:
        return bool(self.get(user_id, event_type)["email_enabled"])

    def should_dashboard(self, user_id: int, event_type: str) -> bool:
        return bool(self.get(user_id, event_type)["dashboard_enabled"])

    # ------------------------------------------------------------------ writes
    def set(self, user_id: int, event_type: str, prefs: dict):
        if event_type not in EVENT_TYPES:
            return False, f"Unknown event type: {event_type}."

        db = get_session()
        try:
            row = (
                db.query(NotificationPreference)
                .filter(
                    NotificationPreference.user_id == user_id,
                    NotificationPreference.event_type == event_type,
                )
                .first()
            )
            if row is None:
                row = NotificationPreference(
                    user_id=user_id,
                    event_type=event_type,
                    dashboard_enabled=prefs.get("dashboard_enabled", True),
                    email_enabled=prefs.get("email_enabled", True),
                    timing=prefs.get("timing", 0),
                )
                db.add(row)
            else:
                row.dashboard_enabled = prefs.get("dashboard_enabled", row.dashboard_enabled)
                row.email_enabled = prefs.get("email_enabled", row.email_enabled)
                row.timing = prefs.get("timing", row.timing)
            db.commit()
            return True, "Preferences saved."
        finally:
            db.close()
