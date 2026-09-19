print(">>> report_service.py V2 <<<")

import os
import sys
from datetime import datetime
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
        os.makedirs(REPORTS_DIR, exist_ok=True)

    # ------------------------------------------------------------------ public
    def generate_property_report(self):
        rows = self.properties.list_all()
        headers = ["ID", "Address", "Type", "Status", "Build Details"]
        data = [[
            str(p.property_id),
            p.address or "",
            p.property_type or "",
            p.status or "",
            (p.build_details or "")[:60],
        ] for p in rows]
        return self._build_pdf("Property Report", headers, data)

    def generate_payment_report(self):
        rows = self.payments.list_all()
        headers = ["ID", "Lease", "Amount", "Due", "Paid", "Status"]
        data = [[
            str(p.payment_id),
            str(p.lease_id),
            f"R{p.amount:.2f}" if p.amount is not None else "",
            str(p.due_date) if p.due_date else "",
            str(p.paid_date) if p.paid_date else "—",
            p.status or "",
        ] for p in rows]
        return self._build_pdf("Payment Report", headers, data)

    def generate_lease_report(self):
        rows = self.leases.list_all()
        headers = ["ID", "Property", "Tenant", "Start", "End", "Rent", "Status"]
        data = [[
            str(l.lease_id),
            str(l.property_id),
            str(l.tenant_id),
            str(l.start_date) if l.start_date else "",
            str(l.end_date) if l.end_date else "",
            f"R{l.rent_amount:.2f}" if l.rent_amount is not None else "",
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

    # ------------------------------------------------------------------ internals
    def _build_pdf(self, title, headers, data):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = title.replace(" ", "_")
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