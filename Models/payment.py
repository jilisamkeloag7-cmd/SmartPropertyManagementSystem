from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    lease_id   = Column(Integer, ForeignKey("leases.lease_id"), nullable=False)
    amount     = Column(Float, nullable=False)
    due_date   = Column(Date, nullable=False)
    paid_date  = Column(Date, nullable=True)
    status     = Column(String(30), default="Pending")   # Pending / Paid / Overdue
    created_at = Column(DateTime, default=datetime.utcnow)

    lease = relationship("Lease", back_populates="payments")