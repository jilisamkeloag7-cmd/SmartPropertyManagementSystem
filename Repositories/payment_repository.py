print(">>> payment_repository.py V1 <<<")

from Database.connection import get_session
from Models.payment import Payment


class PaymentRepository:
    def list_all(self):
        db = get_session()
        try:
            return db.query(Payment).order_by(Payment.payment_id).all()
        finally:
            db.close()

    def list_for_lease(self, lease_id: int):
        db = get_session()
        try:
            return (
                db.query(Payment)
                .filter(Payment.lease_id == lease_id)
                .order_by(Payment.due_date)
                .all()
            )
        finally:
            db.close()

    def find_by_id(self, payment_id: int):
        db = get_session()
        try:
            return db.query(Payment).filter(Payment.payment_id == payment_id).first()
        finally:
            db.close()

    def find_pending(self):
        db = get_session()
        try:
            return db.query(Payment).filter(Payment.status == "Pending").all()
        finally:
            db.close()

    def create(self, lease_id, amount, due_date, status="Pending"):
        db = get_session()
        try:
            p = Payment(
                lease_id=lease_id,
                amount=amount,
                due_date=due_date,
                status=status,
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            return p
        finally:
            db.close()

    def mark_paid(self, payment_id: int, paid_date) -> bool:
        db = get_session()
        try:
            p = db.query(Payment).filter(Payment.payment_id == payment_id).first()
            if not p:
                return False
            p.paid_date = paid_date
            p.status = "Paid"
            db.commit()
            return True
        finally:
            db.close()

    def set_status(self, payment_id: int, status: str) -> bool:
        db = get_session()
        try:
            p = db.query(Payment).filter(Payment.payment_id == payment_id).first()
            if not p:
                return False
            p.status = status
            db.commit()
            return True
        finally:
            db.close()