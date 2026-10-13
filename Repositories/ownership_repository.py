
from Database.connection import get_session
from Models.ownership import Ownership


class OwnershipRepository:
    def list_all(self):
        db = get_session()
        try:
            return db.query(Ownership).order_by(Ownership.ownership_id).all()
        finally:
            db.close()

    def list_for_property(self, property_id: int):
        db = get_session()
        try:
            return (
                db.query(Ownership)
                .filter(Ownership.property_id == property_id)
                .order_by(Ownership.ownership_id)
                .all()
            )
        finally:
            db.close()

    def list_for_owner(self, user_id: int):
        """Only currently-active ownerships (end_date IS NULL)."""
        db = get_session()
        try:
            return (
                db.query(Ownership)
                .filter(Ownership.user_id == user_id, Ownership.end_date.is_(None))
                .all()
            )
        finally:
            db.close()

    def property_ids_for_owner(self, user_id: int):
        return [o.property_id for o in self.list_for_owner(user_id)]

    def find_by_id(self, ownership_id: int):
        db = get_session()
        try:
            return (
                db.query(Ownership)
                .filter(Ownership.ownership_id == ownership_id)
                .first()
            )
        finally:
            db.close()

    def sum_active_shares(self, property_id: int) -> float:
        db = get_session()
        try:
            rows = (
                db.query(Ownership)
                .filter(
                    Ownership.property_id == property_id,
                    Ownership.end_date.is_(None),
                )
                .all()
            )
            return sum(o.ownership_share or 0.0 for o in rows)
        finally:
            db.close()

    def create(self, property_id, user_id, share, start_date, end_date=None):
        db = get_session()
        try:
            o = Ownership(
                property_id=property_id,
                user_id=user_id,
                ownership_share=share,
                start_date=start_date,
                end_date=end_date,
            )
            db.add(o)
            db.commit()
            db.refresh(o)
            return o
        finally:
            db.close()

    def close(self, ownership_id: int, end_date) -> bool:
        db = get_session()
        try:
            o = db.query(Ownership).filter(
                Ownership.ownership_id == ownership_id
            ).first()
            if not o:
                return False
            o.end_date = end_date
            db.commit()
            return True
        finally:
            db.close()
