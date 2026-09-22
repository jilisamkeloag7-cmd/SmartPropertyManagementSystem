print(">>> property_detail_dialog.py V3 <<<")

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from Controllers.property_controller import PropertyController
from Controllers.review_controller import ReviewController
from Controllers.viewing_controller import ViewingController
from ui import theme


IMAGE_W = 620
IMAGE_H = 340


class PropertyDetailDialog(QDialog):
    def __init__(self, parent=None, property_data: dict | None = None,
                 session_user: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.session_user = session_user or {}
        self.controller = PropertyController()
        self.review_controller = ReviewController()
        self.viewing_controller = ViewingController()
        self.images = []
        self.current_index = 0

        pid = self.property_data.get("property_id")
        if pid:
            try:
                self.images = self.controller.list_images(pid)
            except Exception:
                self.images = []

        self.setWindowTitle(self.property_data.get("address", "Property"))
        self.setFixedSize(720, 820)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; }}
        """)
        self._build()
        self._render_image()
        self._load_reviews()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {theme.BG_APP}; }}")

        content = QWidget()
        content.setStyleSheet(f"background: {theme.BG_APP};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        # ---- Title row + Request Viewing
        title_row = QHBoxLayout()

        addr = QLabel(self.property_data.get("address", "Property"))
        addr.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        addr.setWordWrap(True)
        title_row.addWidget(addr, stretch=1)

        # Request Viewing button — tenant only, viewable property only
        role = self.session_user.get("role", "")
        status = self.property_data.get("status", "")
        show_viewing_btn = (
            role == "Tenant" and status in ("Available", "Under Maintenance")
        )

        self.btn_request_viewing = QPushButton("📅  Request Viewing")
        self.btn_request_viewing.setCursor(Qt.PointingHandCursor)
        self.btn_request_viewing.setFixedHeight(38)
        self.btn_request_viewing.setStyleSheet(theme.button_qss("primary"))
        self.btn_request_viewing.clicked.connect(self._on_request_viewing)
        self.btn_request_viewing.setVisible(show_viewing_btn)
        title_row.addWidget(self.btn_request_viewing)

        layout.addLayout(title_row)

        # ---- Image area
        img_frame = QFrame()
        img_frame.setFixedHeight(IMAGE_H)
        img_frame.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
            }}
        """)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(8, 8, 8, 8)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            f"background: {theme.BG_SUBTLE}; "
            f"border-radius: {theme.RADIUS_MD}px; "
            f"font-size: 64px; color: {theme.TEXT_FAINT};"
        )
        img_layout.addWidget(self.image_label)
        layout.addWidget(img_frame)

        # ---- Image nav
        nav = QHBoxLayout()
        nav.addStretch()

        self.btn_prev = QPushButton("← Previous")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setFixedHeight(34)
        self.btn_prev.setStyleSheet(theme.button_qss("secondary"))
        self.btn_prev.clicked.connect(self._on_prev)
        nav.addWidget(self.btn_prev)

        self.counter = QLabel("0 / 0")
        self.counter.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_BASE}px; "
            f"padding: 0 12px;"
        )
        nav.addWidget(self.counter)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedHeight(34)
        self.btn_next.setStyleSheet(theme.button_qss("secondary"))
        self.btn_next.clicked.connect(self._on_next)
        nav.addWidget(self.btn_next)

        nav.addStretch()
        layout.addLayout(nav)

        # ---- Details card
        details_frame = QFrame()
        details_frame.setStyleSheet(theme.card_qss())
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(18, 14, 18, 14)
        details_layout.setSpacing(8)

        def kv(label, value):
            row = QHBoxLayout()
            l1 = QLabel(label)
            l1.setFixedWidth(120)
            l1.setStyleSheet(
                f"color: {theme.TEXT_MUTED}; font-weight: bold; "
                f"font-size: {theme.FS_SM}px;"
            )
            l2 = QLabel(str(value or "—"))
            l2.setWordWrap(True)
            l2.setStyleSheet(
                f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px;"
            )
            row.addWidget(l1)
            row.addWidget(l2, stretch=1)
            details_layout.addLayout(row)

        d = self.property_data
        price = d.get("listing_price")
        price_str = f"R{price:,.2f} / month" if price else "—"
        kv("Rent:", price_str)
        kv("Type:", d.get("property_type", ""))
        kv("Status:", d.get("status", ""))
        kv("Details:", d.get("build_details", ""))

        layout.addWidget(details_frame)

        # ---- Reviews section
        reviews_header = QHBoxLayout()

        self.reviews_title = QLabel("Reviews")
        self.reviews_title.setStyleSheet(
            f"font-size: {theme.FS_LG}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        reviews_header.addWidget(self.reviews_title)
        reviews_header.addStretch()

        self.btn_write_review = QPushButton("✎  Write Review")
        self.btn_write_review.setCursor(Qt.PointingHandCursor)
        self.btn_write_review.setFixedHeight(34)
        self.btn_write_review.setStyleSheet(theme.button_qss("primary"))
        self.btn_write_review.clicked.connect(self._on_write_review)
        reviews_header.addWidget(self.btn_write_review)

        layout.addLayout(reviews_header)

        self.reviews_container = QWidget()
        self.reviews_container.setStyleSheet("background: transparent;")
        self.reviews_layout = QVBoxLayout(self.reviews_container)
        self.reviews_layout.setContentsMargins(0, 0, 0, 0)
        self.reviews_layout.setSpacing(8)
        layout.addWidget(self.reviews_container)

        layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet(theme.button_qss("secondary"))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

        outer.addWidget(scroll)

    # ------------------------------------------------------------------ image gallery
    def _render_image(self):
        total = len(self.images)
        if total == 0:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("🏠")
            self.counter.setText("0 / 0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        img = self.images[self.current_index]
        path = img.get("full_path")
        if path and os.path.isfile(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    IMAGE_W, IMAGE_H - 16, Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled)
                self.image_label.setText("")
            else:
                self.image_label.setText("🖼")
        else:
            self.image_label.setText("🖼")

        self.counter.setText(f"{self.current_index + 1} / {total}")
        self.btn_prev.setEnabled(total > 1)
        self.btn_next.setEnabled(total > 1)

    def _on_prev(self):
        if not self.images:
            return
        self.current_index = (self.current_index - 1) % len(self.images)
        self._render_image()

    def _on_next(self):
        if not self.images:
            return
        self.current_index = (self.current_index + 1) % len(self.images)
        self._render_image()

    # ------------------------------------------------------------------ viewing
    def _on_request_viewing(self):
        from ui.viewing_request_dialog import ViewingRequestDialog
        dlg = ViewingRequestDialog(self, property_data=self.property_data)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.viewing_controller.request(
                self.property_data.get("property_id"),
                data["preferred_date"],
                data["preferred_time"],
                data["message"],
                self.session_user,
            )
            if ok:
                QMessageBox.information(self, "Submitted", msg)
                self.btn_request_viewing.setEnabled(False)
                self.btn_request_viewing.setText("✓ Viewing Requested")
            else:
                QMessageBox.warning(self, "Error", msg)

    # ------------------------------------------------------------------ reviews
    def _load_reviews(self):
        while self.reviews_layout.count():
            item = self.reviews_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        pid = self.property_data.get("property_id")
        if not pid:
            return

        try:
            reviews = self.review_controller.list_for_property(pid)
            avg, count = self.review_controller.average_for_property(pid)
        except Exception:
            reviews, avg, count = [], None, 0

        if avg is not None and count > 0:
            stars = "★" * int(round(avg)) + "☆" * (5 - int(round(avg)))
            self.reviews_title.setText(f"Reviews   {stars}   {avg} ({count})")
        else:
            self.reviews_title.setText("Reviews")

        role = self.session_user.get("role", "")
        can_write = role == "Tenant"
        self.btn_write_review.setVisible(can_write)

        if not reviews:
            empty = QLabel("No reviews yet. Be the first!")
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_BASE}px; "
                f"font-style: italic; padding: 8px;"
            )
            self.reviews_layout.addWidget(empty)
            return

        for r in reviews:
            self.reviews_layout.addWidget(self._make_review_card(r))

    def _make_review_card(self, r: dict):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(4)

        header = QHBoxLayout()
        rating = r.get("rating", 0)
        stars = "★" * rating + "☆" * (5 - rating)
        stars_lbl = QLabel(stars)
        stars_lbl.setStyleSheet(
            f"color: {theme.WARNING}; font-size: {theme.FS_BASE}px; "
            f"letter-spacing: 1px;"
        )
        header.addWidget(stars_lbl)

        name_lbl = QLabel(r.get("reviewer_name", "Anonymous"))
        name_lbl.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_SM}px; "
            f"font-weight: bold; padding-left: 8px;"
        )
        header.addWidget(name_lbl)
        header.addStretch()

        date_lbl = QLabel(str(r.get("created_at", ""))[:10])
        date_lbl.setStyleSheet(
            f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px;"
        )
        header.addWidget(date_lbl)

        role = self.session_user.get("role", "")
        if role in ("Administrator", "Property Manager"):
            del_btn = QPushButton("✕")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setFixedSize(24, 24)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {theme.TEXT_FAINT};
                    border: none;
                    font-size: 14px;
                }}
                QPushButton:hover {{ color: {theme.DANGER}; }}
            """)
            del_btn.setToolTip("Remove this review")
            del_btn.clicked.connect(
                lambda checked=False, rid=r.get("review_id"): self._on_delete_review(rid)
            )
            header.addWidget(del_btn)

        inner.addLayout(header)

        comment = r.get("comment") or "(no comment)"
        comment_lbl = QLabel(comment)
        comment_lbl.setWordWrap(True)
        comment_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px; "
            f"padding-top: 2px;"
        )
        inner.addWidget(comment_lbl)

        return card

    def _on_write_review(self):
        from ui.review_form_dialog import ReviewFormDialog
        pid = self.property_data.get("property_id")
        if not pid:
            return
        dlg = ReviewFormDialog(
            self,
            property_address=self.property_data.get("address", ""),
        )
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.review_controller.create(
                pid, data["rating"], data["comment"], self.session_user
            )
            if ok:
                QMessageBox.information(self, "Thank you", msg)
                self._load_reviews()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_delete_review(self, review_id: int):
        confirm = QMessageBox.question(
            self, "Remove review",
            "Remove this review permanently?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.review_controller.delete(review_id, self.session_user)
        if ok:
            self._load_reviews()
        else:
            QMessageBox.warning(self, "Error", msg)