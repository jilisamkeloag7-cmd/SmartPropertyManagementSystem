print(">>> email_service.py V2 (Brevo API) <<<")

import os
import requests


class EmailService:
    """
    Email dispatcher using Brevo's HTTP API.
    Falls back to console logging if API key is missing (dry-run mode).
    """

    def __init__(self):
        self.api_key = os.environ.get("BREVO_API_KEY", "").strip()
        self.sender_email = os.environ.get("BREVO_SENDER_EMAIL", "").strip()
        self.sender_name = os.environ.get("BREVO_SENDER_NAME", "SPMS").strip()
        self.enabled = bool(self.api_key and self.sender_email)
        self.api_url = "https://api.brevo.com/v3/smtp/email"

        if self.enabled:
            print(f"[email] Brevo API configured (sender: {self.sender_email})")
        else:
            print("[email] Brevo API not configured - running in dry-run mode")

        self._queue = []

    # ------------------------------------------------------------------ send
    def send(self, to: str, subject: str, body: str) -> bool:
        if not to:
            return False
        if not self.enabled:
            print(f"[email] (dry-run) to={to} subject={subject}")
            return True

        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json",
            }
            payload = {
                "sender": {
                    "email": self.sender_email,
                    "name": self.sender_name,
                },
                "to": [{"email": to}],
                "subject": subject,
                "textContent": body,
            }
            response = requests.post(
                self.api_url, json=payload, headers=headers, timeout=10
            )
            if response.status_code in (200, 201, 202):
                print(f"[email] Sent to {to}")
                return True
            print(f"[email] FAILED to {to}. "
                  f"Status {response.status_code}: {response.text[:200]}")
            return False
        except Exception as e:
            print(f"[email] FAILED to {to}: {type(e).__name__}: {e}")
            return False

    # ------------------------------------------------------------------ queue
    def queue(self, notification) -> None:
        """Enqueue an email derived from a Notification object."""
        self._queue.append(notification)

    def flush(self) -> int:
        """Send all queued emails. Returns count sent."""
        items = list(self._queue)
        self._queue.clear()
        sent = 0
        for n in items:
            user_email = self._lookup_email(n)
            if self.send(
                user_email,
                n.title or "Notification",
                n.message or "",
            ):
                sent += 1
        return sent

    # ------------------------------------------------------------------ helper
    def _lookup_email(self, notification):
        try:
            from Repositories.user_repository import UserRepository
            u = UserRepository().find_by_id(notification.user_id)
            return u.email if u else ""
        except Exception:
            return ""
