from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base

class Property(Base):
    __tablename__ = "properties"

    property_id   = Column(Integer, primary_key=True, autoincrement=True)
    address       = Column(String(255), nullable=False)
    property_type = Column(String(50))   # House / Apartment / Commercial
    build_details = Column(Text)         # year, size, rooms, etc.
    status        = Column(String(30), default="Available")  # Available / Occupied / Maintenance
    created_at    = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ownerships   = relationship("Ownership", back_populates="property", cascade="all, delete-orphan")
    leases       = relationship("Lease", back_populates="property", cascade="all, delete-orphan")
    maintenance  = relationship("MaintenanceRequest", back_populates="property", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Property #{self.property_id} {self.address}>"