from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    type            = Column(String(50))       # payment_due / lease_expiring / maintenance_update
    title           = Column(String(150))
    message         = Column(Text)
    priority        = Column(String(20), default="Normal")
    created_at      = Column(DateTime, default=datetime.utcnow)
    read_at         = Column(DateTime, nullable=True)   # None = unread

    user = relationship("User", back_populates="notifications")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    preference_id     = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    event_type        = Column(String(50))     # payment_due / lease_expiring / maintenance
    dashboard_enabled = Column(Boolean, default=True)
    email_enabled     = Column(Boolean, default=True)
    timing            = Column(Integer, default=3)   # days before event

    user = relationship("User", back_populates="preferences")