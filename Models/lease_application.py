
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class LeaseApplication(Base):
    __tablename__ = "lease_applications"

    application_id   = Column(Integer, primary_key=True, autoincrement=True)
    property_id      = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    tenant_id        = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    preferred_start  = Column(Date, nullable=False)
    duration_months  = Column(Integer, nullable=False)
    message          = Column(Text, nullable=True)
    status           = Column(String(30), default="Pending")  # Pending / Approved / Declined / Cancelled
    decision_note    = Column(Text, nullable=True)
    created_lease_id = Column(Integer, ForeignKey("leases.lease_id"), nullable=True)
    decided_at       = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property")
    tenant   = relationship("User")
    lease    = relationship("Lease")

    def __repr__(self):
        return f"<LeaseApplication #{self.application_id} ({self.status})>"
