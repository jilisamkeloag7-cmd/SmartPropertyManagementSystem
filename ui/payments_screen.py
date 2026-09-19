print(">>> payments_screen.py V1 <<<")

from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QBrush, QColor
from Controllers.payment_controller import PaymentController
from ui.payment_form_dialog import PaymentFormDialog


class PaymentsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = PaymentController()
        self.user_data = None
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data
        # On entering, run overdue detection (spec: "invoked daily and on-read")
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
        rows = self.controller.list(filters)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} payment record(s)")

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("💰 Payments")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; "
            "font-size: 13px; padding: 6px 10px;"
        )
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Add Payment")
        self.btn_add.setFixedHeight(38)
        self.btn_add.setStyleSheet(
            "background-color: #3498db; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # Filters
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by property address or tenant…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Paid", "Overdue"])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.status_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(
            "background: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        btn_refresh.clicked.connect(self.refresh)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        self.count_label = QLabel("0 payment record(s)")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Amount", "Due", "Paid", "Status", "Lease ID"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #ecf0f1;
                border-radius: 12px; font-size: 13px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background: #f8fbfe; color: #2c3e50;
                padding: 10px; border: none;
                font-weight: bold; font-size: 12px;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background: #eaf3fb; color: #2c3e50;
            }
        """)
        hv = self.table.horizontalHeader()
        for i in range(8):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # Actions
        actions = QHBoxLayout()
        actions.addStretch()

        self.btn_mark_paid = QPushButton("Mark Selected as Paid")
        self.btn_mark_paid.setFixedHeight(38)
        self.btn_mark_paid.setStyleSheet(
            "background: #27ae60; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_mark_paid.clicked.connect(self._on_mark_paid)
        actions.addWidget(self.btn_mark_paid)

        layout.addLayout(actions)

    # ------------------------------------------------------------------ helpers
    def _populate_table(self, rows):
        self.table.setRowCount(0)
        overdue_brush = QBrush(QColor("#fdecea"))
        overdue_fg = QBrush(QColor("#c0392b"))

        for r, p in enumerate(rows):
            self.table.insertRow(r)
            cells = [
                str(p["payment_id"]),
                p["property_address"] or "",
                p["tenant_name"] or "",
                f"R{p['amount']:.2f}" if p["amount"] is not None else "",
                str(p["due_date"]) if p["due_date"] else "",
                str(p["paid_date"]) if p["paid_date"] else "—",
                p["status"] or "",
                str(p["lease_id"]),
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if p["status"] == "Overdue":
                    item.setBackground(overdue_brush)
                    item.setForeground(overdue_fg)
                self.table.setItem(r, c, item)

    def _selected_payment_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_add(self):
        dlg = PaymentFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_mark_paid(self):
        pid = self._selected_payment_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a payment first.")
            return
        confirm = QMessageBox.question(
            self, "Mark paid",
            f"Mark payment #{pid} as Paid (today)?",
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