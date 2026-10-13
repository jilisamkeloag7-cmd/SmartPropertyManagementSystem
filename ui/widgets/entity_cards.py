
from datetime import date
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QProgressBar, QWidget)
from PySide6.QtCore import Qt
from ui import theme


# =====================================================================
# Helpers
# =====================================================================
def _status_badge(text, kind="info"):
    colors = {
        "info":    (theme.INFO_SOFT, theme.INFO),
        "success": (theme.SUCCESS_SOFT, theme.SUCCESS_HOVER),
        "warning": (theme.WARNING_SOFT, theme.WARNING_HOVER),
        "danger":  (theme.DANGER_SOFT, theme.DANGER_HOVER),
        "muted":   (theme.BG_SUBTLE, theme.TEXT_MUTED),
    }
    bg, fg = colors.get(kind, colors["info"])
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        background: {bg};
        color: {fg};
        padding: 3px 10px;
        border-radius: {theme.RADIUS_SM}px;
        font-size: {theme.FS_XS}px;
        font-weight: bold;
    """)
    return lbl


def _priority_badge(text):
    colors = {
        "Low":    (theme.BG_SUBTLE, theme.TEXT_FAINT),
        "Medium": (theme.INFO_SOFT, theme.INFO),
        "High":   (theme.WARNING_SOFT, theme.WARNING_HOVER),
        "Urgent": (theme.DANGER_SOFT, theme.DANGER_HOVER),
    }
    bg, fg = colors.get(text, colors["Low"])
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        background: {bg};
        color: {fg};
        padding: 3px 10px;
        border-radius: {theme.RADIUS_SM}px;
        font-size: {theme.FS_XS}px;
        font-weight: bold;
    """)
    return lbl


def _money(value):
    if value is None:
        return "—"
    return f"R{value:,.2f}"


def _date_str(d):
    if not d:
        return "—"
    return str(d)


def _hairline():
    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {theme.BORDER};")
    return line


# =====================================================================
# Month section header (used by tenant payments)
# =====================================================================
class MonthSectionHeader(QWidget):
    """
    Header row:  'September 2026  ─────────────  Paid R6,500 / R8,500 billed'
    """

    def __init__(self, label: str, summary: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size: {theme.FS_LG}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(lbl)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {theme.BORDER};")
        layout.addWidget(line, stretch=1)

        if summary:
            smry = QLabel(summary)
            smry.setStyleSheet(
                f"font-size: {theme.FS_XS}px; color: {theme.TEXT_MUTED}; "
                f"font-weight: bold;"
            )
            layout.addWidget(smry)


# =====================================================================
# Tenant Lease Card — rent as hero + progress bar
# =====================================================================
class TenantLeaseCard(QFrame):
    def __init__(self, lease: dict, on_request_termination=None, parent=None):
        super().__init__(parent)
        self.lease = lease
        self.on_request_termination = on_request_termination
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        self.setMinimumWidth(340)
        self.setMinimumHeight(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        # ---- Header
        header = QHBoxLayout()
        header.setSpacing(10)

        icon = QLabel("🏠")
        icon.setStyleSheet("font-size: 22px;")
        header.addWidget(icon)

        addr = QLabel(self.lease.get("property_address") or "Property")
        addr.setWordWrap(True)
        addr.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(addr, stretch=1)

        status = self.lease.get("status", "")
        kind = {"Active": "success", "Expired": "muted",
                "Terminated": "danger"}.get(status, "info")
        header.addWidget(_status_badge(status, kind))
        layout.addLayout(header)

        layout.addSpacing(4)

        # ---- Rent (hero)
        rent_lbl = QLabel(_money(self.lease.get("rent_amount")))
        rent_lbl.setStyleSheet(
            f"font-size: 34px; font-weight: bold; color: {theme.PRIMARY};"
        )
        layout.addWidget(rent_lbl)

        per_month = QLabel("per month")
        per_month.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(per_month)

        layout.addSpacing(6)

        # ---- Lease period with progress bar
        start = self.lease.get("start_date")
        end = self.lease.get("end_date")
        if start and end:
            today = date.today()
            total_days = max(1, (end - start).days)
            elapsed = max(0, min(total_days, (today - start).days))
            pct = int(elapsed / total_days * 100)

            meta = QHBoxLayout()
            term_lbl = QLabel(f"Term progress")
            term_lbl.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
                f"font-weight: bold;"
            )
            meta.addWidget(term_lbl)
            meta.addStretch()
            pct_lbl = QLabel(f"{pct}%")
            pct_lbl.setStyleSheet(
                f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_XS}px; "
                f"font-weight: bold;"
            )
            meta.addWidget(pct_lbl)
            layout.addLayout(meta)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {theme.BG_SUBTLE};
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background: {theme.PRIMARY};
                    border-radius: 4px;
                }}
            """)
            layout.addWidget(bar)

            dates = QHBoxLayout()
            s_lbl = QLabel(_date_str(start))
            s_lbl.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px;"
            )
            e_lbl = QLabel(_date_str(end))
            e_lbl.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px;"
            )
            dates.addWidget(s_lbl)
            dates.addStretch()
            dates.addWidget(e_lbl)
            layout.addLayout(dates)

        # ---- Pending termination banner
        if self.lease.get("termination_requested"):
            banner = QLabel("⚠  Termination request pending manager approval")
            banner.setWordWrap(True)
            banner.setStyleSheet(f"""
                background: {theme.WARNING_SOFT};
                color: {theme.WARNING_HOVER};
                padding: 8px 10px;
                border-radius: {theme.RADIUS_SM}px;
                font-size: {theme.FS_XS}px;
                font-weight: bold;
            """)
            layout.addWidget(banner)

        layout.addStretch()

        # ---- Action
        if status == "Active" and not self.lease.get("termination_requested"):
            btn = QPushButton("Request Termination")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet(theme.button_qss("warning"))
            btn.clicked.connect(self._handle_action)
            layout.addWidget(btn)

    def _handle_action(self):
        if self.on_request_termination:
            self.on_request_termination(self.lease)


# =====================================================================
# Tenant Payment Card
# =====================================================================
class TenantPaymentCard(QFrame):
    def __init__(self, payment: dict, on_mark_paid=None, parent=None):
        super().__init__(parent)
        self.payment = payment
        self.on_mark_paid = on_mark_paid
        self._build()

    def _build(self):
        status = self.payment.get("status", "")

        # Accent border tinted by status
        accent = {
            "Paid": "#10b981",
            "Pending": "#3b82f6",
            "Overdue": "#ef4444",
            "Awaiting Confirmation": "#f59e0b",
        }.get(status, theme.BORDER)

        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {accent};
                border-radius: {theme.RADIUS_LG}px;
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        icon = QLabel("💰")
        icon.setStyleSheet("font-size: 20px;")
        header.addWidget(icon)

        title = QLabel("Rent Payment")
        title.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title, stretch=1)

        kind = {"Paid": "success", "Pending": "info",
                "Overdue": "danger",
                "Awaiting Confirmation": "warning"}.get(status, "muted")
        header.addWidget(_status_badge(status, kind))
        layout.addLayout(header)

        # Property (small subtitle)
        prop = self.payment.get("property_address") or ""
        if prop:
            prop_lbl = QLabel(prop)
            prop_lbl.setWordWrap(True)
            prop_lbl.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px;"
            )
            layout.addWidget(prop_lbl)

        layout.addSpacing(4)

        # Amount (hero)
        amount = QLabel(_money(self.payment.get("amount")))
        amount.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(amount)

        # Due date
        due = QLabel(f"Due {_date_str(self.payment.get('due_date'))}")
        due.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(due)

        # Paid date
        if self.payment.get("paid_date"):
            paid = QLabel(f"✓  Paid {_date_str(self.payment.get('paid_date'))}")
            paid.setStyleSheet(
                f"color: {theme.SUCCESS_HOVER}; font-size: {theme.FS_SM}px; "
                f"font-weight: bold;"
            )
            layout.addWidget(paid)

        # Reference
        ref = self.payment.get("payment_reference")
        if ref and status == "Awaiting Confirmation":
            ref_lbl = QLabel(f"Ref: {ref[:60]}")
            ref_lbl.setWordWrap(True)
            ref_lbl.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px; "
                f"font-style: italic;"
            )
            layout.addWidget(ref_lbl)

        layout.addStretch()

        # Action
        if status in ("Pending", "Overdue"):
            btn = QPushButton("I've Paid This")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet(theme.button_qss("success"))
            btn.clicked.connect(self._handle_action)
            layout.addWidget(btn)

    def _handle_action(self):
        if self.on_mark_paid:
            self.on_mark_paid(self.payment)


# =====================================================================
# Tenant Viewing Card
# =====================================================================
class TenantViewingCard(QFrame):
    def __init__(self, viewing: dict, on_cancel=None, parent=None):
        super().__init__(parent)
        self.viewing = viewing
        self.on_cancel = on_cancel
        self._build()

    def _build(self):
        status = self.viewing.get("status", "")
        accent = {
            "Pending": "#f59e0b",
            "Approved": "#10b981",
            "Declined": "#ef4444",
            "Cancelled": "#94a3b8",
        }.get(status, theme.BORDER)

        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {accent};
                border-radius: {theme.RADIUS_LG}px;
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        self.setMinimumWidth(320)
        self.setMinimumHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        header = QHBoxLayout()
        icon = QLabel("📅")
        icon.setStyleSheet("font-size: 20px;")
        header.addWidget(icon)

        addr = QLabel(self.viewing.get("property_address") or "Property")
        addr.setWordWrap(True)
        addr.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(addr, stretch=1)

        kind = {"Pending": "warning", "Approved": "success",
                "Declined": "danger", "Cancelled": "muted"}.get(status, "info")
        header.addWidget(_status_badge(status, kind))
        layout.addLayout(header)

        when = QLabel(
            f"{_date_str(self.viewing.get('preferred_date'))}  ·  "
            f"{self.viewing.get('preferred_time') or '—'}"
        )
        when.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(when)

        msg = self.viewing.get("message")
        if msg:
            msg_lbl = QLabel(msg[:120])
            msg_lbl.setWordWrap(True)
            msg_lbl.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
            )
            layout.addWidget(msg_lbl)

        note = self.viewing.get("manager_note")
        if note:
            note_lbl = QLabel(f"📩 {note[:140]}")
            note_lbl.setWordWrap(True)
            note_lbl.setStyleSheet(f"""
                background: {theme.BG_SUBTLE};
                color: {theme.TEXT_MAIN};
                padding: 8px;
                border-radius: {theme.RADIUS_SM}px;
                font-size: {theme.FS_XS}px;
            """)
            layout.addWidget(note_lbl)

        layout.addStretch()

        if status == "Pending" and self.on_cancel:
            btn = QPushButton("Cancel Request")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setStyleSheet(theme.button_qss("secondary"))
            btn.clicked.connect(lambda: self.on_cancel(self.viewing))
            layout.addWidget(btn)


# =====================================================================
# Tenant Application Card — with progress tracker
# =====================================================================
class TenantApplicationCard(QFrame):
    def __init__(self, app: dict, on_withdraw=None, parent=None):
        super().__init__(parent)
        self.app = app
        self.on_withdraw = on_withdraw
        self._build()

    def _build(self):
        status = self.app.get("status", "")
        accent = {
            "Pending": "#f59e0b",
            "Approved": "#10b981",
            "Declined": "#ef4444",
            "Cancelled": "#94a3b8",
        }.get(status, theme.BORDER)

        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-left: 4px solid {accent};
                border-radius: {theme.RADIUS_LG}px;
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        self.setMinimumWidth(360)
        self.setMinimumHeight(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        icon = QLabel("📝")
        icon.setStyleSheet("font-size: 20px;")
        header.addWidget(icon)

        addr = QLabel(self.app.get("property_address") or "Property")
        addr.setWordWrap(True)
        addr.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(addr, stretch=1)

        kind = {"Pending": "warning", "Approved": "success",
                "Declined": "danger", "Cancelled": "muted"}.get(status, "info")
        header.addWidget(_status_badge(status, kind))
        layout.addLayout(header)

        # Details
        start = _date_str(self.app.get("preferred_start"))
        duration = self.app.get("duration_months")
        meta = QLabel(f"Start {start}  ·  {duration} months")
        meta.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(meta)

        layout.addSpacing(6)

        # ---- Progress tracker
        # Stages: Submitted (1) → Reviewed (2) → Approved (3) → Signed (4)
        # Pending = stage 1 or 2 (submitted/reviewed)
        # Approved = stage 3
        # Declined/Cancelled = grey out all
        if status == "Pending":
            current_stage = 2
        elif status == "Approved":
            current_stage = 3
        else:
            current_stage = 0

        tracker = QHBoxLayout()
        tracker.setSpacing(0)

        stages = ["Submitted", "Under Review", "Approved", "Signed"]

        for i, name in enumerate(stages):
            col = QVBoxLayout()
            col.setSpacing(4)

            dot = QLabel("●")
            if i < current_stage - 1:
                dot.setStyleSheet(f"color: {theme.SUCCESS}; font-size: 14px;")
            elif i == current_stage - 1:
                dot.setStyleSheet(f"color: {theme.PRIMARY}; font-size: 14px;")
            else:
                dot.setStyleSheet(f"color: {theme.BORDER}; font-size: 14px;")
            dot.setAlignment(Qt.AlignCenter)
            col.addWidget(dot)

            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                f"font-size: {theme.FS_XS}px; "
                f"color: {theme.TEXT_MUTED if i >= current_stage else theme.TEXT_MAIN};"
            )
            col.addWidget(lbl)

            tracker.addLayout(col, stretch=1)

            # Connecting line (except after last)
            if i < len(stages) - 1:
                line = QFrame()
                line.setFixedHeight(2)
                if i < current_stage - 1:
                    line.setStyleSheet(f"background: {theme.SUCCESS};")
                else:
                    line.setStyleSheet(f"background: {theme.BORDER};")
                line.setFixedWidth(30)
                tracker.addWidget(line, alignment=Qt.AlignTop)

        layout.addLayout(tracker)

        # Decision note
        note = self.app.get("decision_note")
        if note:
            note_lbl = QLabel(f"📩 {note[:140]}")
            note_lbl.setWordWrap(True)
            note_lbl.setStyleSheet(f"""
                background: {theme.BG_SUBTLE};
                color: {theme.TEXT_MAIN};
                padding: 8px;
                border-radius: {theme.RADIUS_SM}px;
                font-size: {theme.FS_XS}px;
            """)
            layout.addWidget(note_lbl)

        layout.addStretch()

        # Action
        if status == "Pending" and self.on_withdraw:
            btn = QPushButton("Withdraw Application")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setStyleSheet(theme.button_qss("secondary"))
            btn.clicked.connect(lambda: self.on_withdraw(self.app))
            layout.addWidget(btn)


# =====================================================================
# Maintenance Kanban Card (used by tenant + manager)
# =====================================================================
class MaintenanceKanbanCard(QFrame):
    def __init__(self, request: dict, on_click=None, parent=None):
        super().__init__(parent)
        self.request = request
        self.on_click = on_click
        self._build()

    def _build(self):
        priority = self.request.get("priority", "Low")
        accent = {
            "Low": "#94a3b8",
            "Medium": "#0ea5e9",
            "High": "#f59e0b",
            "Urgent": "#ef4444",
        }.get(priority, theme.BORDER)

        self.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-left: 3px solid {accent};
                border-radius: {theme.RADIUS_MD}px;
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header
        header = QHBoxLayout()
        rid = QLabel(f"#{self.request.get('request_id')}")
        rid.setStyleSheet(
            f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold;"
        )
        header.addWidget(rid)
        header.addStretch()
        header.addWidget(_priority_badge(priority))
        layout.addLayout(header)

        # Property
        addr = QLabel(self.request.get("property_address") or "")
        addr.setWordWrap(True)
        addr.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_SM}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(addr)

        # Description snippet
        desc = (self.request.get("description") or "")[:80]
        if len(self.request.get("description", "")) > 80:
            desc += "…"
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px;"
        )
        layout.addWidget(desc_lbl)

        # Submitter (only shown to manager)
        submitter = self.request.get("submitter_name")
        if submitter:
            sub_lbl = QLabel(f"👤 {submitter}")
            sub_lbl.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px;"
            )
            layout.addWidget(sub_lbl)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click(self.request)
        super().mousePressEvent(event)


# =====================================================================
# Kanban Column container
# =====================================================================
class KanbanColumn(QFrame):
    """One column of the maintenance kanban board."""

    def __init__(self, title: str, colour: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.colour = colour
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            KanbanColumn {{
                background: {theme.BG_SUBTLE};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
        """)
        self.setMinimumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(10)

        # Column header
        header = QHBoxLayout()
        header.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {self.colour}; font-size: 12px;")
        header.addWidget(dot)

        title_lbl = QLabel(self.title)
        title_lbl.setStyleSheet(
            f"font-size: {theme.FS_BASE}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title_lbl)
        header.addStretch()

        self.count_lbl = QLabel("0")
        self.count_lbl.setStyleSheet(f"""
            background: {theme.BG_CARD};
            color: {theme.TEXT_MUTED};
            padding: 2px 8px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        header.addWidget(self.count_lbl)

        layout.addLayout(header)

        # Cards container
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()
        layout.addWidget(self.cards_container, stretch=1)

    def clear(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def add_card(self, card: QWidget):
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def set_count(self, n: int):
        self.count_lbl.setText(str(n))
