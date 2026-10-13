print(">>> email_service.py V3 <<<")

import os
import re
import threading
import requests


_FAKE_DOMAINS = (".local", ".test", ".example", ".invalid")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_real_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        return False
    if any(email.endswith(d) for d in _FAKE_DOMAINS):
        return False
    return True


class EmailService:
    _logged = False  # class-level flag: log only once per session

    def __init__(self):
        self.api_key = os.environ.get("BREVO_API_KEY", "").strip()
        self.sender_email = os.environ.get("BREVO_SENDER_EMAIL", "").strip()
        self.sender_name = os.environ.get("BREVO_SENDER_NAME", "SPMS").strip()
        self.enabled = bool(self.api_key and self.sender_email)
        self.api_url = "https://api.brevo.com/v3/smtp/email"

        if not EmailService._logged:
            if self.enabled:
                print(f"[email] Brevo API configured (sender: {self.sender_email})")
            else:
                print("[email] Brevo API not configured - dry-run mode")
            EmailService._logged = True

    def _send_sync(self, to: str, subject: str, body: str) -> bool:
        try:
            headers = {
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json",
            }
            payload = {
                "sender": {"email": self.sender_email, "name": self.sender_name},
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
            print(f"[email] FAILED to {to}. {response.status_code}: {response.text[:150]}")
            return False
        except Exception as e:
            print(f"[email] FAILED to {to}: {type(e).__name__}: {e}")
            return False

    def send(self, to: str, subject: str, body: str) -> bool:
        if not to:
            return False
        if not _is_real_email(to):
            print(f"[email] (skipped - not a real address) {to}")
            return True
        if not self.enabled:
            print(f"[email] (dry-run) to={to} subject={subject}")
            return True

        t = threading.Thread(
            target=self._send_sync, args=(to, subject, body), daemon=True
        )
        t.start()
        return True

    def queue(self, notification) -> None:
        try:
            from Repositories.user_repository import UserRepository
            u = UserRepository().find_by_id(notification.user_id)
            if u:
                self.send(u.email, notification.title or "Notification",
                          notification.message or "")
        except Exception as e:
            print(f"[email] queue failed: {e}")

    def flush(self) -> int:
        return 0