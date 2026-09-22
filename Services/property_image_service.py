print(">>> property_image_service.py V2 <<<")

import os
import shutil
import uuid
import sys
from Repositories.property_image_repository import PropertyImageRepository


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MAX_SIZE_MB = 5
WRITE_ROLES = {"Administrator", "Property Manager"}


def _images_dir() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Assets", "property_images")


IMAGES_DIR = _images_dir()


class PropertyImageService:
    def __init__(self):
        self.images = PropertyImageRepository()
        os.makedirs(IMAGES_DIR, exist_ok=True)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to manage property images."
        return True, None

    # ------------------------------------------------------------------ reads
    def list_for_property(self, property_id: int):
        rows = self.images.list_for_property(property_id)
        return [
            {
                "image_id": r.image_id,
                "property_id": r.property_id,
                "filename": r.filename,
                "order_index": r.order_index,
                "uploaded_at": r.uploaded_at,
                "full_path": os.path.join(IMAGES_DIR, r.filename),
            }
            for r in rows
        ]

    def first_image_path(self, property_id: int):
        rows = self.images.list_for_property(property_id)
        if not rows:
            return None
        full = os.path.join(IMAGES_DIR, rows[0].filename)
        return full if os.path.isfile(full) else None

    # ------------------------------------------------------------------ writes
    def add_image(self, property_id: int, source_path: str, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        if not os.path.isfile(source_path):
            return False, "File not found."

        ext = os.path.splitext(source_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type ({ext}). Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"

        size_mb = os.path.getsize(source_path) / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            return False, f"File is too large ({size_mb:.1f} MB). Max {MAX_SIZE_MB} MB."

        # Filename pattern: p{property_id}_{uuid}.{ext}
        # This lets the seed script auto-relink images to properties after a reseed.
        new_name = f"p{property_id}_{uuid.uuid4().hex}{ext}"
        dest = os.path.join(IMAGES_DIR, new_name)

        try:
            shutil.copy2(source_path, dest)
        except Exception as e:
            return False, f"Failed to save image: {e}"

        order_index = self.images.count_for_property(property_id)
        self.images.create(property_id, new_name, order_index)

        return True, "Image added."

    def remove_image(self, image_id: int, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        img = self.images.find_by_id(image_id)
        if not img:
            return False, "Image not found."

        path = os.path.join(IMAGES_DIR, img.filename)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass

        self.images.delete(image_id)
        return True, "Image removed."