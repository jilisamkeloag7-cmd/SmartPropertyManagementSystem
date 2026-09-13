from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    request_id   = Column(Integer, primary_key=True, autoincrement=True)
    property_id  = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    description  = Column(Text, nullable=False)
    priority     = Column(String(20), default="Medium")   # Low / Medium / High / Urgent
    status       = Column(String(30), default="Open")     # Open / In Progress / Resolved / Closed
    created_at   = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    property  = relationship("Property", back_populates="maintenance")
    submitter = relationship("User", back_populates="maintenance")