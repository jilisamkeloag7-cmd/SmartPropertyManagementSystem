print(">>> profile_service.py V1 <<<")

import os
import shutil
import uuid
import sys

from Repositories.user_repository import UserRepository
from Repositories.profile_change_repository import ProfileChangeRepository
from Services.security import (hash_password, verify_password,
                                hash_answer, normalise_answer)
from Services.notification_service import NotificationService


MANAGER_ROLES = {"Administrator", "Property Manager"}

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_MB = 3

# Directly editable fields (no approval)
DIRECT_FIELDS = {"phone", "security_question", "security_answer", "password"}

# Fields needing approval
APPROVAL_FIELDS = {"name", "email"}


def _profile_images_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        internal = os.path.join(exe_dir, "_internal")
        base = internal if os.path.isdir(internal) else exe_dir
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "Assets", "profile_images")


PROFILE_IMAGES_DIR = _profile_images_dir()


class ProfileService:
    def __init__(self):
        self.users = UserRepository()
        self.changes = ProfileChangeRepository()
        self.notifications = NotificationService()
        os.makedirs(PROFILE_IMAGES_DIR, exist_ok=True)

    # ------------------------------------------------------------------ reads
    def get_profile(self, user_id: int):
        u = self.users.find_by_id(user_id)
        if not u:
            return None
        return {
            "user_id": u.user_id,
            "id_number": u.id_number,
            "name": u.name,
            "email": u.email,
            "phone": u.phone or "",
            "role": u.role.value,
            "status": u.status,
            "created_at": u.created_at,
            "security_question": u.security_question or "",
            "profile_image": u.profile_image,
            "profile_image_path": self._full_image_path(u.profile_image),
        }

    def _full_image_path(self, filename: str | None):
        if not filename:
            return None
        full = os.path.join(PROFILE_IMAGES_DIR, filename)
        return full if os.path.isfile(full) else None

    def list_pending_requests(self):
        rows = self.changes.list_pending()
        return [self._enrich(r) for r in rows]

    def list_all_requests(self):
        rows = self.changes.list_all()
        return [self._enrich(r) for r in rows]

    def list_my_requests(self, user_id: int):
        rows = self.changes.list_for_user(user_id)
        return [self._enrich(r) for r in rows]

    def _enrich(self, r):
        u = self.users.find_by_id(r.user_id)
        decider = self.users.find_by_id(r.decided_by) if r.decided_by else None
        return {
            "request_id": r.request_id,
            "user_id": r.user_id,
            "user_name": u.name if u else "",
            "user_email": u.email if u else "",
            "user_role": u.role.value if u else "",
            "field_name": r.field_name,
            "old_value": r.old_value or "",
            "new_value": r.new_value or "",
            "reason": r.reason or "",
            "status": r.status,
            "requested_at": r.requested_at,
            "decided_at": r.decided_at,
            "decided_by": r.decided_by,
            "decider_name": decider.name if decider else "",
            "decision_note": r.decision_note or "",
        }

    # ------------------------------------------------------------------ direct updates
    def update_phone(self, user_id: int, phone: str):
        phone = (phone or "").strip()
        if phone and (not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit()):
            return False, "Phone number should contain digits only."
        if len(phone) > 20:
            return False, "Phone number is too long."
        self.users.update_phone(user_id, phone)
        return True, "Phone number updated."

    def update_security_qa(self, user_id: int, question: str, answer: str):
        if not question:
            return False, "Please choose a security question."
        if len((answer or "").strip()) < 3:
            return False, "Security answer must be at least 3 characters."
        self.users.update_security_answer(user_id, question, hash_answer(answer))
        return True, "Security question updated."

    def change_password(self, user_id: int, old_password: str,
                         new_password: str, confirm_password: str):
        if not old_password or not new_password:
            return False, "Please fill in both password fields."
        if new_password != confirm_password:
            return False, "New passwords don't match."
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."

        u = self.users.find_by_id(user_id)
        if not u:
            return False, "Account not found."
        if not verify_password(old_password, u.password_hash):
            return False, "Current password is incorrect."

        self.users.update_password(user_id, hash_password(new_password))
        return True, "Password changed."

    # ------------------------------------------------------------------ profile image
        def upload_profile_image(self, user_id: int, source_path: str):
         if not os.path.isfile(source_path):
            return False, "File not found."

         ext = os.path.splitext(source_path)[1].lower()
         if ext not in SUPPORTED_EXTENSIONS:
             return False, f"Unsupported file type."

         size_mb = os.path.getsize(source_path) / (1024 * 1024)
         if size_mb > MAX_IMAGE_MB:
             return False, f"File is too large ({size_mb:.1f} MB)."

         new_name = f"u{user_id}_{uuid.uuid4().hex}{ext}"

         # ---- Cloud
         from Database.config import USE_CLOUD_STORAGE
         from Services.cloud_storage_service import get_cloud_storage
         if USE_CLOUD_STORAGE:
             cloud = get_cloud_storage()
             url = cloud.upload_profile_image(source_path, new_name)
             if url:
                 self.users.update_profile_image(user_id, url)
                 return True, "Profile picture uploaded to cloud."

         # ---- Local fallback
         u = self.users.find_by_id(user_id)
         if u and u.profile_image and not u.profile_image.startswith("http"):
             old = os.path.join(PROFILE_IMAGES_DIR, u.profile_image)
             try:
                 if os.path.isfile(old):
                     os.remove(old)
             except OSError:
                 pass

        dest = os.path.join(PROFILE_IMAGES_DIR, new_name)
        try:
            shutil.copy2(source_path, dest)
        except Exception as e:
            return False, f"Failed to save image: {e}"

        self.users.update_profile_image(user_id, new_name)
        return True, "Profile picture updated."
    # ------------------------------------------------------------------ change requests
    def request_change(self, user_id: int, field_name: str, new_value: str,
                        reason: str):
        if field_name not in APPROVAL_FIELDS:
            return False, "This field cannot be changed here."

        new_value = (new_value or "").strip()
        if not new_value:
            return False, "New value cannot be empty."
        if len(new_value) > 120:
            return False, "Value is too long."

        u = self.users.find_by_id(user_id)
        if not u:
            return False, "Account not found."

        # Validate email format
        if field_name == "email":
            if "@" not in new_value:
                return False, "Please enter a valid email."
            # Check uniqueness
            existing = self.users.find_by_email(new_value)
            if existing and existing.user_id != user_id:
                return False, "Another account already uses that email."

        # Prevent duplicate pending requests for the same field
        if self.changes.find_pending_for_field(user_id, field_name):
            return False, f"A pending change request already exists for {field_name}."

        old_value = u.name if field_name == "name" else u.email

        self.changes.create(user_id, field_name, old_value, new_value, reason)

        # Notify managers and admins
        for mgr in self.users.list_all():
            if mgr.role.value in MANAGER_ROLES:
                self.notifications.emit(
                    user_id=mgr.user_id,
                    type="profile_change_request",
                    title=f"Profile change request — {u.name}",
                    message=(f"{u.name} has requested to change their "
                             f"{field_name} from '{old_value}' to '{new_value}'."),
                    priority="Normal",
                )

        return True, "Change request submitted. A manager will review it shortly."

    def cancel_request(self, request_id: int, session_user: dict):
        r = self.changes.find_by_id(request_id)
        if not r:
            return False, "Request not found."
        if r.user_id != session_user.get("user_id"):
            return False, "You can only cancel your own requests."
        if r.status != "Pending":
            return False, f"Cannot cancel a {r.status.lower()} request."

        self.changes.set_status(request_id, "Cancelled",
                                decided_by=session_user.get("user_id"),
                                decision_note="Cancelled by user.")
        return True, "Request cancelled."

    def approve_change(self, request_id: int, session_user: dict):
        if session_user.get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can approve requests."

        r = self.changes.find_by_id(request_id)
        if not r:
            return False, "Request not found."
        if r.status != "Pending":
            return False, f"Request is already {r.status}."

        u = self.users.find_by_id(r.user_id)
        if not u:
            return False, "User no longer exists."

        # Apply the change
        if r.field_name == "name":
            self.users.update_name_and_email(u.user_id, r.new_value, u.email)
        elif r.field_name == "email":
            self.users.update_name_and_email(u.user_id, u.name, r.new_value)

        self.changes.set_status(request_id, "Approved",
                                decided_by=session_user.get("user_id"),
                                decision_note="Approved.")

        # Notify user
        self.notifications.emit(
            user_id=r.user_id,
            type="profile_change_approved",
            title="Profile change approved",
            message=f"Your {r.field_name} change has been approved.",
            priority="Normal",
        )
        return True, f"{r.field_name.title()} change approved."

    def reject_change(self, request_id: int, reason: str, session_user: dict):
        if session_user.get("role") not in MANAGER_ROLES:
            return False, "Only managers or administrators can reject requests."

        r = self.changes.find_by_id(request_id)
        if not r:
            return False, "Request not found."
        if r.status != "Pending":
            return False, f"Request is already {r.status}."

        reason = (reason or "").strip()
        if len(reason) < 3:
            return False, "Please provide a reason (at least 3 characters)."

        self.changes.set_status(request_id, "Rejected",
                                decided_by=session_user.get("user_id"),
                                decision_note=reason)

        self.notifications.emit(
            user_id=r.user_id,
            type="profile_change_rejected",
            title="Profile change rejected",
            message=f"Your {r.field_name} change was declined. Reason: {reason}",
            priority="High",
        )
        return True, "Request rejected."

    def pending_count(self) -> int:
        return self.changes.pending_count()