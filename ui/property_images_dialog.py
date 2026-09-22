print(">>> property_images_dialog.py V1 <<<")

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QWidget, QFileDialog,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from Controllers.property_controller import PropertyController
from ui import theme


THUMB_W = 160
THUMB_H = 120
THUMB_COLS = 3
THUMB_GAP = 12


class PropertyImagesDialog(QDialog):
    """Manage images for a single property."""

    def __init__(self, parent=None, property_id: int = None,
                 property_address: str = "", session_user: dict = None):
        super().__init__(parent)
        self.property_id = property_id
        self.property_address = property_address
        self.session_user = session_user or {}
        self.controller = PropertyController()
        self.setWindowTitle(f"Images — {property_address}")
        self.setFixedSize(620, 560)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; }}
        """)
        self._build()
        self._load()

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Property Images")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
        header.addStretch()

        btn_add = QPushButton("+ Add Images")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedHeight(36)
        btn_add.setStyleSheet(theme.button_qss("primary"))
        btn_add.clicked.connect(self._on_add)
        header.addWidget(btn_add)

        layout.addLayout(header)

        # Subtitle
        subtitle = QLabel(
            f"Uploaded images appear on the property card and detail view. "
            f"Maximum {5} MB per image."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        # Scroll area for thumbnails
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {theme.BG_APP}; }}")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet(f"background: {theme.BG_APP};")
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(THUMB_GAP)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll, stretch=1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(38)
        btn_close.setStyleSheet(theme.button_qss("secondary"))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    # ------------------------------------------------------------------ load
    def _load(self):
        # Clear existing thumbs
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.property_id:
            return

        images = self.controller.list_images(self.property_id)

        if not images:
            empty = QLabel(
                "No images yet.\nClick \"+ Add Images\" to upload photos."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_MD}px; "
                f"padding: 40px;"
            )
            self.grid.addWidget(empty, 0, 0)
            return

        for i, img in enumerate(images):
            thumb = self._make_thumb(img)
            row = i // THUMB_COLS
            col = i % THUMB_COLS
            self.grid.addWidget(thumb, row, col)

    def _make_thumb(self, img: dict):
        wrapper = QFrame()
        wrapper.setFixedSize(THUMB_W, THUMB_H + 40)
        wrapper.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)

        inner = QVBoxLayout(wrapper)
        inner.setContentsMargins(6, 6, 6, 6)
        inner.setSpacing(6)

        # Image thumbnail
        thumb_lbl = QLabel()
        thumb_lbl.setFixedSize(THUMB_W - 12, THUMB_H - 12)
        thumb_lbl.setAlignment(Qt.AlignCenter)
        thumb_lbl.setStyleSheet(
            f"background: {theme.BG_SUBTLE}; "
            f"border-radius: {theme.RADIUS_SM}px;"
        )

        path = img.get("full_path")
        if path and os.path.isfile(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    thumb_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                thumb_lbl.setPixmap(scaled)
        else:
            thumb_lbl.setText("🖼")

        inner.addWidget(thumb_lbl)

        # Remove button
        btn_remove = QPushButton("Remove")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setFixedHeight(28)
        btn_remove.setStyleSheet(theme.button_qss("danger"))
        btn_remove.clicked.connect(
            lambda checked=False, iid=img["image_id"]: self._on_remove(iid)
        )
        inner.addWidget(btn_remove)

        return wrapper

    # ------------------------------------------------------------------ handlers
    def _on_add(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp);;All Files (*)",
        )
        if not files:
            return

        success_count = 0
        errors = []
        for f in files:
            ok, msg = self.controller.add_image(
                self.property_id, f, self.session_user
            )
            if ok:
                success_count += 1
            else:
                errors.append(f"{os.path.basename(f)}: {msg}")

        if success_count:
            QMessageBox.information(
                self, "Added",
                f"{success_count} image(s) added successfully."
            )
        if errors:
            QMessageBox.warning(
                self, "Some images rejected",
                "\n".join(errors[:5])  # cap at 5 for readability
            )

        self._load()

    def _on_remove(self, image_id: int):
        confirm = QMessageBox.question(
            self, "Remove image",
            "Remove this image? The file will be deleted permanently.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.remove_image(image_id, self.session_user)
        if ok:
            self._load()
        else:
            QMessageBox.warning(self, "Error", msg)