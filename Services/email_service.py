print(">>> email_service.py V1 <<<")

import os
import smtplib
import threading
from email.mime.text import MIMEText
from datetime import datetime


class EmailService:
    """
    SMTP dispatcher. If SMTP_* env vars are missing, the service operates
    in "dry-run" mode: it logs to console but does not attempt to send.
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_addr = os.getenv("SMTP_FROM", self.smtp_user or "noreply@spm.local")
        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_pass)

        # Simple in-memory queue (thread-safe via GIL — sufficient for a desktop app)
        self._queue = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ public
    def send(self, to: str, subject: str, body: str) -> bool:
        if not to:
            return False
        if not self.enabled:
            print(f"[email] (dry-run) to={to} subject={subject}")
            return True

        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = to

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as s:
                s.starttls()
                s.login(self.smtp_user, self.smtp_pass)
                s.send_message(msg)
            print(f"[email] sent to {to}")
            return True
        except Exception as e:
            print(f"[email] FAILED to {to}: {e}")
            return False

    def queue(self, notification) -> None:
        """Enqueue an email derived from a Notification object."""
        with self._lock:
            self._queue.append(notification)

    def flush(self) -> int:
        """Send all queued emails. Returns count sent."""
        with self._lock:
            items = list(self._queue)
            self._queue.clear()

        sent = 0
        for n in items:
            ok = self.send(
                to=self._lookup_email(n),
                subject=n.title or "Notification",
                body=n.message or "",
            )
            if ok:
                sent += 1
        return sent

    # ------------------------------------------------------------------ helpers
    def _lookup_email(self, notification):
        try:
            from Repositories.user_repository import UserRepository
            u = UserRepository().find_by_id(notification.user_id)
            return u.email if u else ""
        except Exception:
            return ""