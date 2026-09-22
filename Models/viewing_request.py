print(">>> viewing_request.py V1 <<<")

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class ViewingRequest(Base):
    __tablename__ = "viewing_requests"

    request_id     = Column(Integer, primary_key=True, autoincrement=True)
    property_id    = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    tenant_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    preferred_date = Column(Date, nullable=False)
    preferred_time = Column(String(20), nullable=True)     # Morning / Afternoon / Evening
    message        = Column(Text, nullable=True)
    status         = Column(String(30), default="Pending")  # Pending / Approved / Declined / Cancelled
    manager_note   = Column(Text, nullable=True)
    decided_at     = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property")
    tenant   = relationship("User")

    def __repr__(self):
        return f"<ViewingRequest #{self.request_id} ({self.status})>"