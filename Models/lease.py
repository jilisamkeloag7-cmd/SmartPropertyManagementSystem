from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base

class Lease(Base):
    __tablename__ = "leases"

    lease_id    = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    tenant_id   = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    rent_amount = Column(Float, nullable=False)
    status      = Column(String(30), default="Active")   # Active / Expired / Terminated
    created_at  = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="leases")
    tenant   = relationship("User", back_populates="leases")
    payments = relationship("Payment", back_populates="lease", cascade="all, delete-orphan")