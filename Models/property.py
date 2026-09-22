print(">>> property.py V3 <<<")

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class Property(Base):
    __tablename__ = "properties"

    property_id   = Column(Integer, primary_key=True, autoincrement=True)
    address       = Column(String(255), nullable=False)
    property_type = Column(String(50))
    build_details = Column(Text)
    status        = Column(String(30), default="Available")
    listing_price = Column(Float, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ownerships   = relationship("Ownership", back_populates="property",
                                cascade="all, delete-orphan")
    leases       = relationship("Lease", back_populates="property",
                                cascade="all, delete-orphan")
    maintenance  = relationship("MaintenanceRequest", back_populates="property",
                                cascade="all, delete-orphan")
    images       = relationship("PropertyImage", back_populates="property",
                                cascade="all, delete-orphan",
                                order_by="PropertyImage.order_index")

    def __repr__(self):
        return f"<Property #{self.property_id} {self.address}>"