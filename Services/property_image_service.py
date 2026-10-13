
import os
import shutil
import uuid
import sys
from Repositories.property_image_repository import PropertyImageRepository
from Services.cloud_storage_service import get_cloud_storage
from Database.config import USE_CLOUD_STORAGE


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MAX_SIZE_MB = 5
WRITE_ROLES = {"Administrator", "Property Manager"}


def _images_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        internal = os.path.join(exe_dir, "_internal")
        base = internal if os.path.isdir(internal) else exe_dir
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Assets", "property_images")


IMAGES_DIR = _images_dir()


class PropertyImageService:
    def __init__(self):
        self.images = PropertyImageRepository()
        self.cloud = get_cloud_storage()
        os.makedirs(IMAGES_DIR, exist_ok=True)

    @staticmethod
    def _assert_write_permission(session_user):
        if not session_user or session_user.get("role") not in WRITE_ROLES:
            return False, "You do not have permission to manage property images."
        return True, None

    # ------------------------------------------------------------------ reads
    def list_for_property(self, property_id: int):
        rows = self.images.list_for_property(property_id)
        out = []
        for r in rows:
            filename = r.filename
            # If cloud mode: filename is actually a full URL
            if filename and filename.startswith("http"):
                out.append({
                    "image_id": r.image_id,
                    "property_id": r.property_id,
                    "filename": filename,
                    "order_index": r.order_index,
                    "uploaded_at": r.uploaded_at,
                    "full_path": filename,   # URL is directly usable
                    "is_url": True,
                })
            else:
                # Local fallback
                full = os.path.join(IMAGES_DIR, filename)
                out.append({
                    "image_id": r.image_id,
                    "property_id": r.property_id,
                    "filename": filename,
                    "order_index": r.order_index,
                    "uploaded_at": r.uploaded_at,
                    "full_path": full,
                    "is_url": False,
                })
        return out

    def first_image_path(self, property_id: int):
        rows = self.images.list_for_property(property_id)
        if not rows:
            return None
        filename = rows[0].filename
        if filename and filename.startswith("http"):
            return filename      # it's a URL — QPixmap can load URLs? No, need special handling
        full = os.path.join(IMAGES_DIR, filename)
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
            return False, f"Unsupported file type. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"

        size_mb = os.path.getsize(source_path) / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            return False, f"File is too large ({size_mb:.1f} MB). Max {MAX_SIZE_MB} MB."

        new_name = f"p{property_id}_{uuid.uuid4().hex}{ext}"

        # ---- Cloud upload if enabled
        if USE_CLOUD_STORAGE and self.cloud.enabled:
            url = self.cloud.upload_property_image(source_path, new_name)
            if not url:
                return False, "Cloud upload rejected. Check Supabase bucket permissions (RLS policy)."
            order_index = self.images.count_for_property(property_id)
            self.images.create(property_id, url, order_index)
            return True, "Image uploaded to cloud."

        # ---- Local fallback
        dest = os.path.join(IMAGES_DIR, new_name)
        try:
            shutil.copy2(source_path, dest)
        except Exception as e:
            return False, f"Failed to save image: {e}"
        order_index = self.images.count_for_property(property_id)
        self.images.create(property_id, new_name, order_index)
        return True, "Image added locally."

    def remove_image(self, image_id: int, session_user: dict):
        ok, err = self._assert_write_permission(session_user)
        if not ok:
            return False, err

        img = self.images.find_by_id(image_id)
        if not img:
            return False, "Image not found."

        filename = img.filename
        # Cloud delete
        if filename and filename.startswith("http") and self.cloud.enabled:
            # Extract the object path from the URL
            try:
                obj_path = filename.split(f"/{self.cloud_bucket_name()}/")[-1]
                self.cloud.delete_property_image(obj_path)
            except Exception:
                pass
        # Local delete
        else:
            path = os.path.join(IMAGES_DIR, filename)
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass

        self.images.delete(image_id)
        return True, "Image removed."

    @staticmethod
    def cloud_bucket_name():
        from Database.config import SUPABASE_STORAGE_BUCKET
        return SUPABASE_STORAGE_BUCKET
