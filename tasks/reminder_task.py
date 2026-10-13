
from Services.lease_service import LeaseService
from Services.payment_service import PaymentService
from Services.notification_service import NotificationService
from Services.email_service import EmailService
from Services.preference_service import PreferenceService
from Repositories.notification_repository import NotificationRepository


class ReminderTask:
    """Runs the daily housekeeping checks that other modules rely on."""

    def __init__(self):
        self.leases = LeaseService()
        self.payments = PaymentService()
        self.notifications = NotificationService()
        self.emails = EmailService()
        self.preferences = PreferenceService()
        self.notif_repo = NotificationRepository()

    def run(self):
        print(f"[reminder] running at {__import__('datetime').datetime.now()}")

        # 1. Overdue payments → flip + notify
        try:
            count = self.payments.check_overdue()
            print(f"[reminder] {count} payment(s) newly overdue")
        except Exception as e:
            print(f"[reminder] payment check failed: {e}")

        # 2. Lease expiry alerts
        try:
            expiring = self.leases.check_expiring(threshold_days=30)
            for lease in expiring:
                self.notifications.emit(
                    user_id=lease["tenant_id"],
                    type="lease_expiring",
                    title="Lease expiring soon",
                    message=(
                        f"Lease #{lease['lease_id']} for "
                        f"{lease['property_address']} expires on {lease['end_date']}."
                    ),
                    priority="High",
                )
            print(f"[reminder] {len(expiring)} lease(s) flagged for expiry")
        except Exception as e:
            print(f"[reminder] lease check failed: {e}")

        # 3. Flush email queue (dry-run if unconfigured)
        try:
            sent = self.emails.flush()
            print(f"[reminder] {sent} email(s) dispatched")
        except Exception as e:
            print(f"[reminder] email flush failed: {e}")
