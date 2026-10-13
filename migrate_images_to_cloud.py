"""
One-time migration: upload every local property/profile image to Supabase Storage
and update the database to point at the cloud URL.
"""

import os
import sys

from dotenv import load_dotenv
load_dotenv()

from Database.config import USE_CLOUD_STORAGE
from Services.cloud_storage_service import get_cloud_storage
from Database.connection import get_session
from Models.property_image import PropertyImage
from Models.user import User


def migrate_property_images():
    cloud = get_cloud_storage()
    if not cloud.enabled:
        print("Cloud storage not enabled. Check .env")
        return

    base = os.path.join("Assets", "property_images")
    if not os.path.isdir(base):
        print(f"Missing folder: {base}")
        return

    db = get_session()
    try:
        rows = db.query(PropertyImage).all()
        print(f"Found {len(rows)} property image(s) in DB.")
        migrated = 0
        skipped = 0

        for row in rows:
            filename = row.filename
            if filename.startswith("http"):
                skipped += 1
                continue

            local = os.path.join(base, filename)
            if not os.path.isfile(local):
                print(f"  [skip] {filename} ? no local file")
                skipped += 1
                continue

            print(f"  [upload] {filename} ...", end=" ")
            url = cloud.upload_property_image(local, filename)
            if url:
                row.filename = url
                migrated += 1
                print("done")
            else:
                print("FAILED")

        db.commit()
        print(f"\nProperty images: {migrated} uploaded, {skipped} skipped.")
    finally:
        db.close()


def migrate_profile_images():
    cloud = get_cloud_storage()
    if not cloud.enabled:
        return

    base = os.path.join("Assets", "profile_images")
    if not os.path.isdir(base):
        print(f"No profile image folder ? skipping.")
        return

    db = get_session()
    try:
        users = db.query(User).filter(User.profile_image.isnot(None)).all()
        print(f"Found {len(users)} user(s) with profile images.")
        migrated = 0
        skipped = 0

        for u in users:
            filename = u.profile_image
            if filename.startswith("http"):
                skipped += 1
                continue
            local = os.path.join(base, filename)
            if not os.path.isfile(local):
                skipped += 1
                continue

            print(f"  [upload] {filename} ...", end=" ")
            url = cloud.upload_profile_image(local, filename)
            if url:
                u.profile_image = url
                migrated += 1
                print("done")
            else:
                print("FAILED")

        db.commit()
        print(f"\nProfile images: {migrated} uploaded, {skipped} skipped.")
    finally:
        db.close()


if __name__ == "__main__":
    if not USE_CLOUD_STORAGE:
        print("Cloud storage is not configured in .env ? aborting.")
        sys.exit(1)
    migrate_property_images()
    migrate_profile_images()
    print("\nMigration complete.")
