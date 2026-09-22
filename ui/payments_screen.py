print(">>> payments_screen.py V5 <<<")

from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QInputDialog
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.payment_controller import PaymentController
from ui.payment_form_dialog import PaymentFormDialog
from ui.tenant_payment_dialog import TenantPaymentDialog
from ui import theme


class PaymentsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = PaymentController()
        self.user_data = None
        self.is_writer = False       # manager + admin
        self.is_admin = False        # admin only
        self.is_tenant = False
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        role = self.user_data.get("role", "")
        self.is_writer = role in ("Administrator", "Property Manager")
        self.is_admin = role == "Administrator"
        self.is_tenant = role == "Tenant"
        self._apply_role_ui()

        if self.is_writer:
            try:
                self.controller.check_overdue()
            except Exception as e:
                print(f"[payments] overdue check failed: {e}")

        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} payment record(s)")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.header_title = QLabel("💰 Payments")
        self.header_title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(self.header_title)

        self.readonly_badge = QLabel("Read-only")
        self.readonly_badge.setStyleSheet(f"""
            background: {theme.WARNING_SOFT};
            color: {theme.WARNING_HOVER};
            padding: 4px 12px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        self.readonly_badge.setVisible(False)
        header.addWidget(self.readonly_badge)

        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setCursor(Qt.PointingHandCursor)
        btn_dashboard.setFixedHeight(36)
        btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Add Payment")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by property address or tenant…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Pending", "Awaiting Confirmation", "Paid", "Overdue"]
        )
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(theme.input_qss())
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.status_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(theme.button_qss("secondary"))
        btn_refresh.clicked.connect(self.refresh)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        self.count_label = QLabel("0 payment record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Amount", "Due", "Paid", "Status", "Reference"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
                font-size: {theme.FS_BASE}px;
                gridline-color: transparent;
                alternate-background-color: {theme.BG_SUBTLE};
                outline: none;
            }}
            QHeaderView::section {{
                background: {theme.BG_SUBTLE};
                color: {theme.TEXT_MUTED};
                padding: 12px 10px;
                border: none;
                border-bottom: 1px solid {theme.BORDER};
                font-weight: bold;
                font-size: {theme.FS_XS}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item {{ padding: 10px; border: none; }}
            QTableWidget::item:selected {{
                background: {theme.PRIMARY_SOFT};
                color: {theme.TEXT_MAIN};
            }}
        """)
        hv = self.table.horizontalHeader()
        for i in range(8):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(7, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        # Tenant action
        self.btn_tenant_paid = QPushButton("I've Paid This")
        self.btn_tenant_paid.setCursor(Qt.PointingHandCursor)
        self.btn_tenant_paid.setFixedHeight(38)
        self.btn_tenant_paid.setStyleSheet(theme.button_qss("success"))
        self.btn_tenant_paid.clicked.connect(self._on_tenant_mark_paid)
        actions.addWidget(self.btn_tenant_paid)

        # Manager + admin actions
        self.btn_confirm = QPushButton("Confirm Receipt")
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.setFixedHeight(38)
        self.btn_confirm.setStyleSheet(theme.button_qss("success"))
        self.btn_confirm.clicked.connect(self._on_manager_confirm)
        actions.addWidget(self.btn_confirm)

        self.btn_reject = QPushButton("Reject Claim")
        self.btn_reject.setCursor(Qt.PointingHandCursor)
        self.btn_reject.setFixedHeight(38)
        self.btn_reject.setStyleSheet(theme.button_qss("danger"))
        self.btn_reject.clicked.connect(self._on_manager_reject)
        actions.addWidget(self.btn_reject)

        # Admin-only override
        self.btn_mark_paid = QPushButton("Mark Selected as Paid")
        self.btn_mark_paid.setCursor(Qt.PointingHandCursor)
        self.btn_mark_paid.setFixedHeight(38)
        self.btn_mark_paid.setStyleSheet(theme.button_qss("warning"))
        self.btn_mark_paid.setToolTip(
            "Direct override — bypasses the tenant submission workflow. Admin only."
        )
        self.btn_mark_paid.clicked.connect(self._on_mark_paid)
        actions.addWidget(self.btn_mark_paid)

        layout.addLayout(actions)

    def _apply_role_ui(self):
        role = (self.user_data or {}).get("role", "")
        if role == "Administrator":
            self.header_title.setText("💰 All Payments")
            self.readonly_badge.setVisible(False)
        elif role == "Property Manager":
            self.header_title.setText("💰 Payments")
            self.readonly_badge.setVisible(False)
        elif role == "Owner":
            self.header_title.setText("💰 Payments on My Properties")
            self.readonly_badge.setVisible(True)
        elif role == "Tenant":
            self.header_title.setText("💰 My Payments")
            self.readonly_badge.setVisible(False)
        else:
            self.header_title.setText("💰 Payments")
            self.readonly_badge.setVisible(False)

        # Button visibility
        self.btn_tenant_paid.setVisible(self.is_tenant)
        self.btn_add.setVisible(self.is_writer)
        self.btn_confirm.setVisible(self.is_writer)
        self.btn_reject.setVisible(self.is_writer)
        self.btn_mark_paid.setVisible(self.is_admin)   # ← admin only

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        overdue_bg = QBrush(QColor(theme.DANGER_SOFT))
        overdue_fg = QBrush(QColor(theme.DANGER_HOVER))
        awaiting_bg = QBrush(QColor(theme.WARNING_SOFT))
        awaiting_fg = QBrush(QColor(theme.WARNING_HOVER))

        for r, p in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            cells = [
                str(p["payment_id"]),
                p["property_address"] or "",
                p["tenant_name"] or "",
                f"R{p['amount']:.2f}" if p["amount"] is not None else "",
                str(p["due_date"]) if p["due_date"] else "",
                str(p["paid_date"]) if p["paid_date"] else "—",
                p["status"] or "",
                (p.get("payment_reference") or "")[:60],
            ]
            status = p["status"]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if status == "Overdue":
                    item.setBackground(overdue_bg)
                    item.setForeground(overdue_fg)
                elif status == "Awaiting Confirmation":
                    item.setBackground(awaiting_bg)
                    item.setForeground(awaiting_fg)
                self.table.setItem(r, c, item)

    def _selected_payment(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return self.controller.get(int(item.text()))

    def _selected_payment_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_add(self):
        if not self.is_writer:
            return
        dlg = PaymentFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_mark_paid(self):
        if not self.is_admin:
            return
        pid = self._selected_payment_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a payment first.")
            return
        confirm = QMessageBox.question(
            self, "Mark paid directly",
            f"Mark payment #{pid} as Paid (today)?\n\n"
            f"This bypasses the tenant confirmation workflow. "
            f"Use only for offline/cash payments.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.mark_paid(pid, date.today(), self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_manager_confirm(self):
        if not self.is_writer:
            return
        payment = self._selected_payment()
        if not payment:
            QMessageBox.information(self, "No selection", "Select a payment first.")
            return
        if payment["status"] != "Awaiting Confirmation":
            QMessageBox.information(
                self, "Nothing to confirm",
                "This payment is not awaiting confirmation."
            )
            return

        ref = payment.get("payment_reference") or "(no reference)"
        confirm = QMessageBox.question(
            self, "Confirm payment",
            f"Confirm receipt of payment #{payment['payment_id']} "
            f"of R{payment['amount']:.2f}?\n\n"
            f"Tenant reference:\n{ref}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        ok, msg = self.controller.manager_confirm(
            payment["payment_id"], self.user_data
        )
        if ok:
            QMessageBox.information(self, "Confirmed", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_manager_reject(self):
        if not self.is_writer:
            return
        payment = self._selected_payment()
        if not payment:
            QMessageBox.information(self, "No selection", "Select a payment first.")
            return
        if payment["status"] != "Awaiting Confirmation":
            QMessageBox.information(
                self, "Nothing to reject",
                "This payment is not awaiting confirmation."
            )
            return

        reason, ok = QInputDialog.getText(
            self, "Reject claim",
            "Why is this payment claim being rejected?\n"
            "(The tenant will see this reason.)"
        )
        if not ok or len(reason.strip()) < 3:
            return

        confirm = QMessageBox.question(
            self, "Reject claim",
            f"Reject the payment claim for #{payment['payment_id']}?\n\n"
            f"Reason: {reason}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        ok, msg = self.controller.manager_reject(
            payment["payment_id"], reason, self.user_data
        )
        if ok:
            QMessageBox.information(self, "Rejected", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_tenant_mark_paid(self):
        if not self.is_tenant:
            return
        payment = self._selected_payment()
        if not payment:
            QMessageBox.information(self, "No selection", "Select one of your payments.")
            return
        if payment["status"] == "Paid":
            QMessageBox.information(
                self, "Already paid",
                "This payment is already marked as paid."
            )
            return
        if payment["status"] == "Awaiting Confirmation":
            QMessageBox.information(
                self, "Already submitted",
                "You have already marked this payment. Awaiting manager confirmation."
            )
            return

        dlg = TenantPaymentDialog(self, payment_data=payment)
        if dlg.exec():
            ok, msg = self.controller.tenant_mark_paid(
                payment["payment_id"], dlg.get_data()["reference"], self.user_data
            )
            if ok:
                QMessageBox.information(self, "Submitted", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)