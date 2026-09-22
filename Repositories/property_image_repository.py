print(">>> property_image_repository.py V1 <<<")

from Database.connection import get_session
from Models.property_image import PropertyImage


class PropertyImageRepository:
    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(PropertyImage)
                .filter(PropertyImage.property_id == property_id)
                .order_by(PropertyImage.order_index, PropertyImage.image_id)
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, image_id: int):
        db = get_session()
        try:
            return db.query(PropertyImage).filter(
                PropertyImage.image_id == image_id
            ).first()
        finally:
            db.close()

    def count_for_property(self, property_id: int) -> int:
        db = get_session()
        try:
            return (
                db.query(PropertyImage)
                .filter(PropertyImage.property_id == property_id)
                .count()
            )
        finally:
            db.close()

    def create(self, property_id: int, filename: str, order_index: int = 0):
        db = get_session()
        try:
            img = PropertyImage(
                property_id=property_id,
                filename=filename,
                order_index=order_index,
            )
            db.add(img)
            db.commit()
            db.refresh(img)
            return img
        finally:
            db.close()

    def delete(self, image_id: int) -> bool:
        db = get_session()
        try:
            img = db.query(PropertyImage).filter(
                PropertyImage.image_id == image_id
            ).first()
            if not img:
                return False
            db.delete(img)
            db.commit()
            return True
        finally:
            db.close()