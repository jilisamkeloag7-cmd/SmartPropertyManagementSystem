
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt


class NotificationPreferencesDialog(QDialog):
    """Per-event-type delivery preferences for the current user."""

    def __init__(self, parent=None, controller=None, user_id: int | None = None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.setWindowTitle("Notification Preferences")
        self.setFixedSize(600, 480)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; }
        """)
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Notification Preferences")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Choose how you receive each type of alert. "
            "Dashboard = in-app bell. Email = dispatched via the scheduler."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(subtitle)

        # ---- Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Event", "Dashboard", "Email", "Timing (days)"])
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #ecf0f1;
                border-radius: 10px; font-size: 13px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background: #f8fbfe; color: #2c3e50;
                padding: 10px; border: none;
                font-weight: bold; font-size: 12px;
            }
        """)
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.Stretch)
        hv.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # ---- Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet(
            "background: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 8px; font-weight: bold; padding: 0 20px;"
        )
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)

        btn_save = QPushButton("Save Preferences")
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet(
            "background: #3498db; color: white; border: none; "
            "border-radius: 8px; font-weight: bold; padding: 0 20px;"
        )
        btn_save.clicked.connect(self._on_save)
        buttons.addWidget(btn_save)

        layout.addLayout(buttons)

    def _load(self):
        if not self.user_id:
            return
        rows = self.controller.get_preferences(self.user_id)
        self.table.setRowCount(len(rows))

        for r, pref in enumerate(rows):
            # Event name
            name_item = QTableWidgetItem(pref["event_type"].replace("_", " ").title())
            self.table.setItem(r, 0, name_item)

            # Dashboard checkbox
            cb_dash = QCheckBox()
            cb_dash.setChecked(bool(pref["dashboard_enabled"]))
            wrap_d = QHBoxLayout()
            w_d = QPushButton()  # placeholder not used
            wrap_d.addWidget(cb_dash)
            container_d = self._container_for(cb_dash)
            self.table.setCellWidget(r, 1, container_d)

            # Email checkbox
            cb_mail = QCheckBox()
            cb_mail.setChecked(bool(pref["email_enabled"]))
            container_m = self._container_for(cb_mail)
            self.table.setCellWidget(r, 2, container_m)

            # Timing (days) — only meaningful for event with timing > 0
            timing_item = QTableWidgetItem(str(pref.get("timing", 0)))
            timing_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 3, timing_item)

    @staticmethod
    def _container_for(checkbox: QCheckBox):
        from PySide6.QtWidgets import QWidget
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(checkbox)
        w._cb = checkbox   # keep reference
        return w

    def _on_save(self):
        if not self.user_id:
            self.reject()
            return
        for r in range(self.table.rowCount()):
            event = self.table.item(r, 0).text().lower().replace(" ", "_")
            dash_widget = self.table.cellWidget(r, 1)
            mail_widget = self.table.cellWidget(r, 2)

            dash_enabled = dash_widget._cb.isChecked() if dash_widget else True
            mail_enabled = mail_widget._cb.isChecked() if mail_widget else True

            try:
                timing = int(self.table.item(r, 3).text())
            except (TypeError, ValueError, AttributeError):
                timing = 0

            ok, msg = self.controller.set_preference(
                self.user_id,
                event,
                {
                    "dashboard_enabled": dash_enabled,
                    "email_enabled": mail_enabled,
                    "timing": timing,
                },
            )
            if not ok:
                QMessageBox.warning(self, "Error", msg)
                return

        QMessageBox.information(self, "Saved", "Preferences updated.")
        self.accept()
