
from datetime import date, timedelta
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.payment_repository import PaymentRepository
from Repositories.maintenance_repository import MaintenanceRepository
from Repositories.user_repository import UserRepository
from Repositories.ownership_repository import OwnershipRepository


class DashboardService:
    def __init__(self):
        self.properties = PropertyRepository()
        self.leases = LeaseRepository()
        self.payments = PaymentRepository()
        self.maintenance = MaintenanceRepository()
        self.users = UserRepository()
        self.ownerships = OwnershipRepository()

    # ------------------------------------------------------------------ public
    def aggregate_for(self, user: dict) -> dict:
        role = (user or {}).get("role", "")
        uid = (user or {}).get("user_id")

        if role == "Administrator":
            return self._admin_stats()
        if role == "Property Manager":
            return self._manager_stats()
        if role == "Owner":
            return self._owner_stats(uid)
        if role == "Tenant":
            return self._tenant_stats(uid)
        return self._empty_stats(role)

    # ------------------------------------------------------------------ per-role
    @staticmethod
    def _empty_stats(role):
        return {
            "role": role,
            "stats": [],
            "recent_activity": [],
            "upcoming_notifications": [],
        }

    def _admin_stats(self):
        props = self.properties.list_all()
        leases = self.leases.list_all()
        payments = self.payments.list_all()
        maint = self.maintenance.list_all()
        users = self.users.list_all()

        active_leases = sum(1 for l in leases if l.status == "Active")
        overdue = sum(1 for p in payments if p.status == "Overdue")
        open_maint = sum(1 for m in maint if m.status in ("Open", "In Progress"))

        return {
            "role": "Administrator",
            "stats": [
                {"label": "Users",            "value": len(users)},
                {"label": "Properties",       "value": len(props)},
                {"label": "Active Leases",    "value": active_leases},
                {"label": "Overdue Payments", "value": overdue},
                {"label": "Open Maintenance", "value": open_maint},
            ],
            "recent_activity": self._recent_activity(props, leases, payments, maint),
            "upcoming_notifications": self._upcoming(leases, payments, maint),
        }

    def _manager_stats(self):
        props = self.properties.list_all()
        leases = self.leases.list_all()
        maint = self.maintenance.list_all()

        active_leases = sum(1 for l in leases if l.status == "Active")
        open_maint = sum(1 for m in maint if m.status in ("Open", "In Progress"))

        today = date.today()
        horizon = today + timedelta(days=30)
        upcoming_expiries = sum(
            1 for l in leases
            if l.status == "Active" and l.end_date and today <= l.end_date <= horizon
        )

        return {
            "role": "Property Manager",
            "stats": [
                {"label": "Properties Managed",  "value": len(props)},
                {"label": "Active Leases",       "value": active_leases},
                {"label": "Open Maintenance",    "value": open_maint},
                {"label": "Expiring (30 days)",  "value": upcoming_expiries},
            ],
            "recent_activity": self._recent_activity(props, leases, self.payments.list_all(), maint),
            "upcoming_notifications": self._upcoming(leases, self.payments.list_all(), maint),
        }

    def _owner_stats(self, uid):
        owned_pids = set(self.ownerships.property_ids_for_owner(uid))
        leases = [l for l in self.leases.list_all() if l.property_id in owned_pids]
        payments = [p for p in self.payments.list_all() if p.lease_id in {l.lease_id for l in leases}]
        maint = [m for m in self.maintenance.list_all() if m.property_id in owned_pids]

        active_leases = sum(1 for l in leases if l.status == "Active")
        today = date.today()
        due_this_month = sum(
            1 for p in payments
            if p.status == "Pending" and p.due_date and p.due_date.month == today.month
        )

        return {
            "role": "Owner",
            "stats": [
                {"label": "Owned Properties", "value": len(owned_pids)},
                {"label": "Active Leases",    "value": active_leases},
                {"label": "Payments Due",     "value": due_this_month},
                {"label": "Open Maintenance", "value": sum(1 for m in maint if m.status in ("Open", "In Progress"))},
            ],
            "recent_activity": self._recent_activity_from(leases, payments, maint),
            "upcoming_notifications": self._upcoming(leases, payments, maint),
        }

    def _tenant_stats(self, uid):
        leases = [l for l in self.leases.list_for_tenant(uid)]
        active = [l for l in leases if l.status == "Active"]
        lease_ids = {l.lease_id for l in leases}

        payments = [p for p in self.payments.list_all() if p.lease_id in lease_ids]
        maint = [m for m in self.maintenance.list_all() if m.submitted_by == uid]

        next_pending = sorted(
            [p for p in payments if p.status in ("Pending", "Overdue") and p.due_date],
            key=lambda p: p.due_date,
        )

        return {
            "role": "Tenant",
            "stats": [
                {"label": "Active Leases",    "value": len(active)},
                {"label": "Pending Payments", "value": sum(1 for p in payments if p.status == "Pending")},
                {"label": "Overdue Payments", "value": sum(1 for p in payments if p.status == "Overdue")},
                {"label": "Open Requests",    "value": sum(1 for m in maint if m.status in ("Open", "In Progress"))},
            ],
            "recent_activity": self._recent_activity_from(leases, payments, maint),
            "upcoming_notifications": self._upcoming(leases, payments, maint),
        }

    # ------------------------------------------------------------------ helpers
    def _recent_activity(self, props, leases, payments, maint):
        return self._recent_activity_from(leases, payments, maint)

    def _recent_activity_from(self, leases, payments, maint):
        items = []
        # Latest lease
        if leases:
            latest_lease = max(leases, key=lambda l: l.lease_id)
            items.append(f"Lease #{latest_lease.lease_id} ({latest_lease.status})")
        # Latest payment
        if payments:
            latest_pay = max(payments, key=lambda p: p.payment_id)
            items.append(
                f"Payment #{latest_pay.payment_id} — {latest_pay.status} "
                f"R{latest_pay.amount:.2f}"
            )
        # Latest maintenance
        if maint:
            latest_m = max(maint, key=lambda m: m.request_id)
            items.append(f"Maintenance #{latest_m.request_id} — {latest_m.status}")
        return items or ["No activity yet."]

    def _upcoming(self, leases, payments, maint):
        today = date.today()
        horizon = today + timedelta(days=30)
        out = []
        for l in leases:
            if l.status == "Active" and l.end_date and today <= l.end_date <= horizon:
                out.append(f"Lease #{l.lease_id} expires {l.end_date}")
        for p in payments:
            if p.status == "Pending" and p.due_date and today <= p.due_date <= horizon:
                out.append(f"Payment #{p.payment_id} due {p.due_date}")
        for m in maint:
            if m.status == "Open":
                out.append(f"Open request #{m.request_id}")
        return out[:6]  # cap
