print(">>> report_service.py V3 <<<")

import os
import sys
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.payment_repository import PaymentRepository
from Repositories.maintenance_repository import MaintenanceRepository
from Repositories.ownership_repository import OwnershipRepository
from Repositories.user_repository import UserRepository


def _reports_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Documentation", "reports")


REPORTS_DIR = _reports_dir()


class ReportService:
    def __init__(self):
        self.properties = PropertyRepository()
        self.leases = LeaseRepository()
        self.payments = PaymentRepository()
        self.maintenance = MaintenanceRepository()
        self.ownerships = OwnershipRepository()
        self.users = UserRepository()
        os.makedirs(REPORTS_DIR, exist_ok=True)

    # ==================================================================
    # ADMIN / MANAGER REPORTS (whole system)
    # ==================================================================
    def generate_property_report(self):
        rows = self.properties.list_all()
        headers = ["ID", "Address", "Type", "Status", "Price", "Build Details"]
        data = [[
            str(p.property_id),
            p.address or "",
            p.property_type or "",
            p.status or "",
            f"R{p.listing_price:,.2f}" if p.listing_price else "—",
            (p.build_details or "")[:60],
        ] for p in rows]
        return self._build_pdf("Property Report", headers, data)

    def generate_payment_report(self):
        rows = self.payments.list_all()
        headers = ["ID", "Lease", "Amount (R)", "Due", "Paid", "Status"]
        data = [[
            str(p.payment_id),
            str(p.lease_id),
            f"{p.amount:,.2f}" if p.amount is not None else "",
            str(p.due_date) if p.due_date else "",
            str(p.paid_date) if p.paid_date else "—",
            p.status or "",
        ] for p in rows]
        return self._build_pdf("Payment Report", headers, data)

    def generate_lease_report(self):
        rows = self.leases.list_all()
        headers = ["ID", "Property", "Tenant", "Start", "End", "Rent (R)", "Status"]
        data = [[
            str(l.lease_id),
            str(l.property_id),
            str(l.tenant_id),
            str(l.start_date) if l.start_date else "",
            str(l.end_date) if l.end_date else "",
            f"{l.rent_amount:,.2f}" if l.rent_amount is not None else "",
            l.status or "",
        ] for l in rows]
        return self._build_pdf("Lease Report", headers, data)

    def generate_maintenance_report(self):
        rows = self.maintenance.list_all()
        headers = ["ID", "Property", "Submitter", "Priority", "Status", "Created"]
        data = [[
            str(m.request_id),
            str(m.property_id),
            str(m.submitted_by),
            m.priority or "",
            m.status or "",
            str(m.created_at)[:19] if m.created_at else "",
        ] for m in rows]
        return self._build_pdf("Maintenance Report", headers, data)

    def generate_summary_report(self):
        props = self.properties.list_all()
        leases = self.leases.list_all()
        payments = self.payments.list_all()
        maint = self.maintenance.list_all()

        active_leases = sum(1 for l in leases if l.status == "Active")
        overdue = sum(1 for p in payments if p.status == "Overdue")
        pending = sum(1 for p in payments if p.status == "Pending")
        open_maint = sum(1 for m in maint if m.status in ("Open", "In Progress"))

        headers = ["Metric", "Value"]
        data = [
            ["Total Properties", str(len(props))],
            ["Total Leases", str(len(leases))],
            ["Active Leases", str(active_leases)],
            ["Total Payments", str(len(payments))],
            ["Pending Payments", str(pending)],
            ["Overdue Payments", str(overdue)],
            ["Open Maintenance", str(open_maint)],
        ]
        return self._build_pdf("Executive Summary Report", headers, data)

    # ==================================================================
    # OWNER REPORTS (scoped to owned properties)
    # ==================================================================
    def _owner_scope(self, session_user: dict):
        """Return (owned_property_ids, owned_properties, leases, payments) for owner."""
        uid = session_user.get("user_id")
        owned_pids = set(self.ownerships.property_ids_for_owner(uid))

        properties = [p for p in self.properties.list_all()
                      if p.property_id in owned_pids]
        leases = [l for l in self.leases.list_all()
                  if l.property_id in owned_pids]
        lease_ids = {l.lease_id for l in leases}
        payments = [p for p in self.payments.list_all()
                    if p.lease_id in lease_ids]

        return owned_pids, properties, leases, payments

    def generate_owner_summary(self, session_user: dict):
        """Portfolio summary — counts, occupancy, income at a glance."""
        _, properties, leases, payments = self._owner_scope(session_user)

        active_leases = [l for l in leases if l.status == "Active"]
        occupied = sum(1 for p in properties if p.status == "Occupied")
        available = sum(1 for p in properties if p.status == "Available")
        maintenance = sum(1 for p in properties if p.status == "Under Maintenance")
        occupancy_pct = (occupied / len(properties) * 100) if properties else 0.0

        total_paid = sum(p.amount for p in payments if p.status == "Paid")
        total_pending = sum(p.amount for p in payments if p.status == "Pending")
        total_overdue = sum(p.amount for p in payments if p.status == "Overdue")

        headers = ["Metric", "Value"]
        data = [
            ["Total Owned Properties",   str(len(properties))],
            ["Occupied",                 str(occupied)],
            ["Available",                str(available)],
            ["Under Maintenance",        str(maintenance)],
            ["Occupancy Rate",           f"{occupancy_pct:.1f}%"],
            ["Active Leases",            str(len(active_leases))],
            ["Total Rent Collected",     f"R{total_paid:,.2f}"],
            ["Total Rent Pending",       f"R{total_pending:,.2f}"],
            ["Total Rent Overdue",       f"R{total_overdue:,.2f}"],
            ["Net Position (Paid-Owed)", f"R{total_paid - total_overdue:,.2f}"],
        ]
        title = f"Portfolio Summary — {session_user.get('name','Owner')}"
        return self._build_pdf(title, headers, data)

    def generate_owner_income(self, session_user: dict, months_back: int = 12):
        """Month-by-month income from payments on owned properties."""
        _, _, _, payments = self._owner_scope(session_user)

        today = date.today()
        headers = ["Month", "Paid (R)", "Pending (R)", "Overdue (R)", "Total Billed (R)"]
        data = []

        for i in range(months_back - 1, -1, -1):
            month_start = today.replace(day=1) - relativedelta(months=i)
            month_end = month_start + relativedelta(months=1)
            month_label = month_start.strftime("%Y-%m")

            monthly = [
                p for p in payments
                if p.due_date and month_start <= p.due_date < month_end
            ]
            paid = sum(p.amount for p in monthly if p.status == "Paid")
            pending = sum(p.amount for p in monthly if p.status == "Pending")
            overdue = sum(p.amount for p in monthly if p.status == "Overdue")
            total = paid + pending + overdue
            data.append([
                month_label,
                f"{paid:,.2f}",
                f"{pending:,.2f}",
                f"{overdue:,.2f}",
                f"{total:,.2f}",
            ])

        title = f"Owner Income Report — {session_user.get('name','Owner')}"
        return self._build_pdf(title, headers, data)

    def generate_owner_tenants(self, session_user: dict):
        """Every lease on an owned property with tenant + rent details."""
        _, properties, leases, _ = self._owner_scope(session_user)

        prop_by_id = {p.property_id: p for p in properties}
        user_by_id = {u.user_id: u for u in self.users.list_all()}

        headers = ["Property", "Tenant", "Email", "Start", "End", "Rent (R)", "Status"]
        data = []
        for l in leases:
            prop = prop_by_id.get(l.property_id)
            tenant = user_by_id.get(l.tenant_id)
            data.append([
                (prop.address if prop else f"#{l.property_id}")[:40],
                (tenant.name if tenant else "")[:25],
                (tenant.email if tenant else "")[:30],
                str(l.start_date) if l.start_date else "",
                str(l.end_date) if l.end_date else "",
                f"{l.rent_amount:,.2f}" if l.rent_amount else "—",
                l.status or "",
            ])

        title = f"Owner Tenants Report — {session_user.get('name','Owner')}"
        return self._build_pdf(title, headers, data)

    # ==================================================================
    # PDF BUILDER
    # ==================================================================
    def _build_pdf(self, title, headers, data):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = title.replace(" ", "_").replace("—", "-").replace(":", "")
            filename = f"{safe_title}_{timestamp}.pdf"
            filepath = os.path.join(REPORTS_DIR, filename)

            doc = SimpleDocTemplate(
                filepath, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm,
                topMargin=1.5*cm, bottomMargin=1.5*cm,
            )
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "ReportTitle", parent=styles["Heading1"],
                fontSize=18, spaceAfter=6, textColor=colors.HexColor("#2c3e50"),
            )
            meta_style = ParagraphStyle(
                "ReportMeta", parent=styles["Normal"],
                fontSize=9, textColor=colors.HexColor("#7f8c8d"), spaceAfter=16,
            )

            elements = []
            elements.append(Paragraph(title, title_style))
            elements.append(Paragraph(
                f"Smart Property Management System &nbsp;|&nbsp; "
                f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; "
                f"{len(data)} record(s)",
                meta_style,
            ))

            if not data:
                elements.append(Paragraph(
                    "No records to report.",
                    ParagraphStyle("Empty", parent=styles["Normal"],
                                   textColor=colors.HexColor("#95a5a6"))
                ))
            else:
                table_data = [headers] + data
                table = Table(table_data, repeatRows=1)
                style = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#f8fbfe")]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ecf0f1")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ])
                table.setStyle(style)
                elements.append(table)

            doc.build(elements)
            return True, filepath

        except Exception as e:
            return False, f"Failed to generate report: {e}"