from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from Models.base import Base

class Ownership(Base):
    __tablename__ = "ownerships"

    ownership_id    = Column(Integer, primary_key=True, autoincrement=True)
    property_id     = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    user_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    ownership_share = Column(Float, default=1.0)   # 0.0–1.0
    start_date      = Column(Date)
    end_date        = Column(Date)

    property = relationship("Property", back_populates="ownerships")
    owner    = relationship("User", back_populates="ownerships")