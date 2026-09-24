print(">>> profile_change_request.py V1 <<<")

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class ProfileChangeRequest(Base):
    __tablename__ = "profile_change_requests"

    request_id    = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    field_name    = Column(String(50), nullable=False)   # "name", "email"
    old_value     = Column(Text, nullable=True)
    new_value     = Column(Text, nullable=False)
    reason        = Column(Text, nullable=True)
    status        = Column(String(20), default="Pending")  # Pending/Approved/Rejected
    requested_at  = Column(DateTime, default=datetime.utcnow)
    decided_at    = Column(DateTime, nullable=True)
    decided_by    = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    decision_note = Column(Text, nullable=True)

    user    = relationship("User", foreign_keys=[user_id])
    decider = relationship("User", foreign_keys=[decided_by])

    def __repr__(self):
        return f"<ProfileChangeRequest #{self.request_id} {self.field_name}>"