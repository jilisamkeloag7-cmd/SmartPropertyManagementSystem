print(">>> leases_screen.py V2 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from Controllers.lease_controller import LeaseController
from ui.lease_form_dialog import LeaseFormDialog
from ui import theme


class LeasesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = LeaseController()
        self.user_data = None
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} lease record(s)")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("📄 Leases")
        title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setCursor(Qt.PointingHandCursor)
        btn_dashboard.setFixedHeight(36)
        btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Create Lease")
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
        self.status_filter.addItems(["All", "Active", "Expired", "Terminated"])
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

        self.count_label = QLabel("0 lease record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Start", "End", "Rent", "Status", "Property ID"]
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
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_terminate = QPushButton("Terminate Selected")
        self.btn_terminate.setCursor(Qt.PointingHandCursor)
        self.btn_terminate.setFixedHeight(38)
        self.btn_terminate.setStyleSheet(theme.button_qss("danger"))
        self.btn_terminate.clicked.connect(self._on_terminate_selected)
        actions.addWidget(self.btn_terminate)

        layout.addLayout(actions)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for r, l in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            self.table.setItem(r, 0, QTableWidgetItem(str(l["lease_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(l["property_address"] or ""))
            self.table.setItem(r, 2, QTableWidgetItem(l["tenant_name"] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(str(l["start_date"]) if l["start_date"] else ""))
            self.table.setItem(r, 4, QTableWidgetItem(str(l["end_date"]) if l["end_date"] else ""))
            self.table.setItem(r, 5, QTableWidgetItem(f"R{l['rent_amount']:.2f}" if l["rent_amount"] else ""))
            self.table.setItem(r, 6, QTableWidgetItem(l["status"] or ""))
            self.table.setItem(r, 7, QTableWidgetItem(str(l["property_id"])))

    def _selected_lease_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_add(self):
        dlg = LeaseFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
                self.parent_window.properties_screen.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_terminate_selected(self):
        lid = self._selected_lease_id()
        if lid is None:
            QMessageBox.information(self, "No selection", "Select a lease to terminate.")
            return
        confirm = QMessageBox.question(
            self, "Terminate lease",
            f"Terminate lease #{lid}? The property will become Available again.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.terminate(lid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
            self.parent_window.properties_screen.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)