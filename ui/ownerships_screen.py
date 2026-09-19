print(">>> ownerships_screen.py V1 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QBrush, QColor
from Controllers.ownership_controller import OwnershipController
from ui.ownership_form_dialog import OwnershipFormDialog


class OwnershipsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = OwnershipController()
        self.user_data = None
        self.is_writer = False
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data
        role = (user_data or {}).get("role", "")
        self.is_writer = role in ("Administrator", "Property Manager")
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} ownership record(s)")

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()

        self.header_title = QLabel("🔑 Ownership")
        self.header_title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50;"
        )
        header.addWidget(self.header_title)

        self.readonly_badge = QLabel("Read-only")
        self.readonly_badge.setStyleSheet(
            "background: #fef3cd; color: #856404; "
            "padding: 3px 10px; border-radius: 6px; "
            "font-size: 11px; font-weight: bold;"
        )
        self.readonly_badge.setVisible(False)
        header.addWidget(self.readonly_badge)

        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; "
            "font-size: 13px; padding: 6px 10px;"
        )
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Add Ownership")
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
        self.search_input.setPlaceholderText("Search by property address or owner…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Ended"])
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

        self.count_label = QLabel("0 ownership record(s)")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Owner", "Email", "Share", "Start", "End", "Status"]
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

        self.btn_end = QPushButton("End Selected Ownership")
        self.btn_end.setFixedHeight(38)
        self.btn_end.setStyleSheet(
            "background: #e74c3c; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_end.clicked.connect(self._on_end_selected)
        actions.addWidget(self.btn_end)

        layout.addLayout(actions)

    # ------------------------------------------------------------------ role UI
    def _apply_role_ui(self):
        role = (self.user_data or {}).get("role", "")

        if role == "Administrator":
            self.header_title.setText("🔑 All Ownership Records")
            self.readonly_badge.setVisible(False)
        elif role == "Property Manager":
            self.header_title.setText("🔑 Ownership Records")
            self.readonly_badge.setVisible(False)
        elif role == "Owner":
            self.header_title.setText("🔑 My Properties")
            self.readonly_badge.setVisible(True)
        else:
            self.header_title.setText("🔑 Ownership")
            self.readonly_badge.setVisible(False)

        self.btn_add.setVisible(self.is_writer)
        self.btn_end.setVisible(self.is_writer)

    # ------------------------------------------------------------------ helpers
    def _populate_table(self, rows):
        self.table.setRowCount(0)
        ended_bg = QBrush(QColor("#f4f6f7"))
        ended_fg = QBrush(QColor("#95a5a6"))

        for r, o in enumerate(rows):
            self.table.insertRow(r)
            share_str = f"{o['ownership_share'] * 100:.0f}%" if o["ownership_share"] is not None else ""
            cells = [
                str(o["ownership_id"]),
                o["property_address"] or "",
                o["owner_name"] or "",
                o["owner_email"] or "",
                share_str,
                str(o["start_date"]) if o["start_date"] else "",
                str(o["end_date"]) if o["end_date"] else "—",
                "Active" if o["is_active"] else "Ended",
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if not o["is_active"]:
                    item.setBackground(ended_bg)
                    item.setForeground(ended_fg)
                self.table.setItem(r, c, item)

    def _selected_ownership_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_add(self):
        if not self.is_writer:
            return
        dlg = OwnershipFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.add(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_end_selected(self):
        if not self.is_writer:
            return
        oid = self._selected_ownership_id()
        if oid is None:
            QMessageBox.information(self, "No selection", "Select an ownership record first.")
            return
        confirm = QMessageBox.question(
            self, "End ownership",
            f"End ownership #{oid} today? The record will be preserved as history.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.end(oid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)