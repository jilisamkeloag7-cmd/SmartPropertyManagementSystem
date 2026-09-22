print(">>> payment.py V2 <<<")

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    lease_id   = Column(Integer, ForeignKey("leases.lease_id"), nullable=False)
    amount     = Column(Float, nullable=False)
    due_date   = Column(Date, nullable=False)
    paid_date  = Column(Date, nullable=True)      # set when manager confirms
    status     = Column(String(30), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # ---- B6 tenant self-service fields
    tenant_marked_at     = Column(DateTime, nullable=True)  # when tenant claimed payment
    payment_reference    = Column(Text, nullable=True)      # tenant-entered reference / note

    lease = relationship("Lease", back_populates="payments")

    def __repr__(self):
        return f"<Payment #{self.payment_id} ({self.status})>"