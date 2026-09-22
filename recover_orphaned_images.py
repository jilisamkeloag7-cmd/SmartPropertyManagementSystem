print(">>> recover_orphaned_images.py V1 <<<")

"""
Recover orphaned property images.

Scans Assets/property_images/ for files that have no matching row in the
property_images table (typically after a reseed). Prompts to link each
orphan to a property interactively.

Usage:
    python recover_orphaned_images.py
"""

import os
from Database.connection import get_session
from Models.property import Property
from Models.property_image import PropertyImage
from Services.property_image_service import IMAGES_DIR


def main():
    if not os.path.isdir(IMAGES_DIR):
        print(f"[recover] Image folder missing: {IMAGES_DIR}")
        return

    # ---- Load DB state
    db = get_session()
    try:
        linked_filenames = {
            row.filename
            for row in db.query(PropertyImage).all()
        }
        properties = db.query(Property).order_by(Property.property_id).all()
        prop_list = [
            {"id": p.property_id, "address": p.address}
            for p in properties
        ]
    finally:
        db.close()

    if not prop_list:
        print("[recover] No properties found. Run seed first.")
        return

    # ---- Find orphans
    all_files = [
        f for f in os.listdir(IMAGES_DIR)
        if f != ".gitkeep" and os.path.isfile(os.path.join(IMAGES_DIR, f))
    ]
    orphans = [f for f in all_files if f not in linked_filenames]

    if not orphans:
        print("[recover] No orphaned images found. All files are linked.")
        return

    print()
    print("=" * 60)
    print(f"Found {len(orphans)} orphaned image(s).")
    print("=" * 60)
    print()

    # ---- Property chooser
    print("Available properties:")
    for p in prop_list:
        print(f"  [{p['id']:>2}] {p['address']}")
    print()

    linked_count = 0
    skipped = 0

    for filename in orphans:
        print("-" * 60)
        print(f"Image: {filename}")
        size_kb = os.path.getsize(os.path.join(IMAGES_DIR, filename)) / 1024
        print(f"Size:  {size_kb:.1f} KB")
        print()

        response = input(
            "Assign to property ID (or 's' to skip, 'q' to quit): "
        ).strip().lower()

        if response == "q":
            print("\n[recover] Quit by user.")
            break
        if response == "s" or response == "":
            skipped += 1
            continue

        try:
            pid = int(response)
        except ValueError:
            print("  ! Invalid input — skipping this image.")
            skipped += 1
            continue

        if pid not in {p["id"] for p in prop_list}:
            print(f"  ! Property #{pid} does not exist — skipping.")
            skipped += 1
            continue

        # Link it
        db = get_session()
        try:
            order = (
                db.query(PropertyImage)
                .filter(PropertyImage.property_id == pid)
                .count()
            )
            db.add(PropertyImage(
                property_id=pid,
                filename=filename,
                order_index=order,
            ))
            db.commit()
            print(f"  ✓ Linked to property #{pid}.")
            linked_count += 1
        except Exception as e:
            print(f"  ! Failed to link: {e}")
            skipped += 1
        finally:
            db.close()

    print()
    print("=" * 60)
    print(f"Done. Linked: {linked_count}, Skipped: {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()
    