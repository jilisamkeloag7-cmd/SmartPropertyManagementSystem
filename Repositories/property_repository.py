print(">>> property_repository.py V2 <<<")

from sqlalchemy import func
from Database.connection import get_session
from Models.property import Property


class PropertyRepository:
    def list_all(self):
        db = get_session()
        try:
            return db.query(Property).order_by(Property.property_id).all()
        finally:
            db.close()

    def search(self, query: str = "", status_filter: str | None = None):
        db = get_session()
        try:
            q = db.query(Property)
            if query:
                like = f"%{query}%"
                q = q.filter(
                    (Property.address.ilike(like))
                    | (Property.property_type.ilike(like))
                )
            if status_filter and status_filter != "All":
                q = q.filter(Property.status == status_filter)
            return q.order_by(Property.property_id).all()
        finally:
            db.close()

    def find_by_id(self, property_id: int):
        db = get_session()
        try:
            return db.query(Property).filter(
                Property.property_id == property_id
            ).first()
        finally:
            db.close()

    def create(self, address, property_type, build_details, status, listing_price=None):
        db = get_session()
        try:
            prop = Property(
                address=address,
                property_type=property_type,
                build_details=build_details,
                status=status,
                listing_price=listing_price,
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)
            return prop
        finally:
            db.close()

    def update(self, property_id, address, property_type, build_details, status,
               listing_price=None):
        db = get_session()
        try:
            prop = db.query(Property).filter(Property.property_id == property_id).first()
            if not prop:
                return None
            prop.address = address
            prop.property_type = property_type
            prop.build_details = build_details
            prop.status = status
            prop.listing_price = listing_price
            db.commit()
            db.refresh(prop)
            return prop
        finally:
            db.close()

    def set_status(self, property_id: int, status: str) -> bool:
        db = get_session()
        try:
            prop = db.query(Property).filter(Property.property_id == property_id).first()
            if not prop:
                return False
            prop.status = status
            db.commit()
            return True
        finally:
            db.close()

    def has_active_lease(self, property_id: int) -> bool:
        from Models.lease import Lease
        db = get_session()
        try:
            return (
                db.query(Lease)
                .filter(Lease.property_id == property_id, Lease.status == "Active")
                .count()
                > 0
            )
        finally:
            db.close()

    def has_open_maintenance(self, property_id: int) -> bool:
        from Models.maintenance import MaintenanceRequest
        db = get_session()
        try:
            return (
                db.query(MaintenanceRequest)
                .filter(
                    MaintenanceRequest.property_id == property_id,
                    MaintenanceRequest.status.in_(["Open", "In Progress"]),
                )
                .count()
                > 0
            )
        finally:
            db.close()