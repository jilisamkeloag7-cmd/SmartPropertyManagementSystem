print(">>> review_repository.py V1 <<<")

from Database.connection import get_session
from Models.review import Review


class ReviewRepository:
    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(Review)
                .filter(Review.property_id == property_id)
                .order_by(Review.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, review_id: int):
        db = get_session()
        try:
            return db.query(Review).filter(Review.review_id == review_id).first()
        finally:
            db.close()

    def find_by_reviewer_and_property(self, reviewer_id: int, property_id: int):
        db = get_session()
        try:
            return (
                db.query(Review)
                .filter(Review.reviewer_id == reviewer_id,
                        Review.property_id == property_id)
                .first()
            )
        finally:
            db.close()

    def count_for_property(self, property_id: int) -> int:
        db = get_session()
        try:
            return db.query(Review).filter(Review.property_id == property_id).count()
        finally:
            db.close()

    def average_for_property(self, property_id: int):
        db = get_session()
        try:
            reviews = (
                db.query(Review)
                .filter(Review.property_id == property_id)
                .all()
            )
            if not reviews:
                return None, 0
            avg = sum(r.rating for r in reviews) / len(reviews)
            return round(avg, 1), len(reviews)
        finally:
            db.close()

    def create(self, property_id, reviewer_id, rating, comment):
        db = get_session()
        try:
            r = Review(
                property_id=property_id,
                reviewer_id=reviewer_id,
                rating=rating,
                comment=comment,
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            return r
        finally:
            db.close()

    def update(self, review_id, rating, comment):
        db = get_session()
        try:
            r = db.query(Review).filter(Review.review_id == review_id).first()
            if not r:
                return None
            r.rating = rating
            r.comment = comment
            db.commit()
            db.refresh(r)
            return r
        finally:
            db.close()

    def delete(self, review_id: int) -> bool:
        db = get_session()
        try:
            r = db.query(Review).filter(Review.review_id == review_id).first()
            if not r:
                return False
            db.delete(r)
            db.commit()
            return True
        finally:
            db.close()