print(">>> properties_screen.py V1 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt
from Controllers.property_controller import PropertyController
from ui.property_form_dialog import PropertyFormDialog


class PropertiesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = PropertyController()
        self.user_data = None
        self._build()

    # ------------------------------------------------------------------ API
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
        self.count_label.setText(f"{len(rows)} property record(s)")

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("🏠 Properties")
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

        self.btn_add = QPushButton("+ Add Property")
        self.btn_add.setFixedHeight(38)
        self.btn_add.setStyleSheet(
            "background-color: #3498db; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # Filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address or type…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Available", "Occupied", "Under Maintenance", "Archived"]
        )
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

        # Count label
        self.count_label = QLabel("0 property record(s)")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Address", "Type", "Status", "Build Details"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._on_row_double_click)
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
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # Actions row
        actions = QHBoxLayout()
        actions.addStretch()

        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setStyleSheet(
            "background: #3498db; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_edit.clicked.connect(self._on_edit_selected)
        actions.addWidget(self.btn_edit)

        self.btn_archive = QPushButton("Archive Selected")
        self.btn_archive.setFixedHeight(38)
        self.btn_archive.setStyleSheet(
            "background: #e74c3c; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_archive.clicked.connect(self._on_archive_selected)
        actions.addWidget(self.btn_archive)

        layout.addLayout(actions)

    # ------------------------------------------------------------------ helpers
    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for r, p in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(p["property_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(p["address"] or ""))
            self.table.setItem(r, 2, QTableWidgetItem(p["property_type"] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(p["status"] or ""))
            self.table.setItem(r, 4, QTableWidgetItem(p["build_details"] or ""))

    def _selected_property_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_add(self):
        dlg = PropertyFormDialog(self, property_data=None)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a property to edit.")
            return
        data = self.controller.get(pid)
        if not data:
            QMessageBox.warning(self, "Error", "Property not found.")
            return
        dlg = PropertyFormDialog(self, property_data=data)
        if dlg.exec():
            ok, msg = self.controller.update(pid, dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_archive_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a property to archive.")
            return
        confirm = QMessageBox.question(
            self, "Archive property",
            f"Archive property #{pid}? It will no longer appear as active.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.archive(pid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_edit_selected()