print(">>> cloud_storage_service.py V1 <<<")

import os
from Database.config import (USE_CLOUD_STORAGE, SUPABASE_URL,
                              SUPABASE_ANON_KEY, SUPABASE_STORAGE_BUCKET,
                              SUPABASE_PROFILE_BUCKET)


class CloudStorageService:
    """
    Wrapper around Supabase Storage. Silently falls back to None when
    credentials are missing (offline/demo mode).
    """

    def __init__(self):
        self.enabled = USE_CLOUD_STORAGE
        self.client = None
        if self.enabled:
            try:
                from supabase import create_client
                self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                print("[cloud-storage] connected")
            except Exception as e:
                print(f"[cloud-storage] init failed: {e}")
                self.enabled = False

    # ------------------------------------------------------------------ upload
    def upload_property_image(self, local_path: str, cloud_name: str) -> str | None:
        if not self.enabled:
            return None
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            ext = os.path.splitext(local_path)[1].lower()
            mime = {
                ".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".gif": "image/gif",
                ".webp": "image/webp", ".bmp": "image/bmp",
            }.get(ext, "application/octet-stream")

            self.client.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
                path=cloud_name,
                file=data,
                file_options={"content-type": mime, "upsert": "true"},
            )
            # Build the public URL
            public_url = self.client.storage.from_(
                SUPABASE_STORAGE_BUCKET
            ).get_public_url(cloud_name)
            return public_url
        except Exception as e:
            print(f"[cloud-storage] upload failed: {e}")
            return None

    def upload_profile_image(self, local_path: str, cloud_name: str) -> str | None:
        if not self.enabled:
            return None
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            ext = os.path.splitext(local_path)[1].lower()
            mime = {
                ".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(ext, "application/octet-stream")

            self.client.storage.from_(SUPABASE_PROFILE_BUCKET).upload(
                path=cloud_name,
                file=data,
                file_options={"content-type": mime, "upsert": "true"},
            )
            return self.client.storage.from_(
                SUPABASE_PROFILE_BUCKET
            ).get_public_url(cloud_name)
        except Exception as e:
            print(f"[cloud-storage] profile upload failed: {e}")
            return None

    def delete_property_image(self, cloud_name: str) -> bool:
        if not self.enabled:
            return False
        try:
            self.client.storage.from_(SUPABASE_STORAGE_BUCKET).remove([cloud_name])
            return True
        except Exception:
            return False

    def delete_profile_image(self, cloud_name: str) -> bool:
        if not self.enabled:
            return False
        try:
            self.client.storage.from_(SUPABASE_PROFILE_BUCKET).remove([cloud_name])
            return True
        except Exception:
            return False


# Singleton
_cloud = None

def get_cloud_storage() -> CloudStorageService:
    global _cloud
    if _cloud is None:
        _cloud = CloudStorageService()
    return _cloud