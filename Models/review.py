print(">>> review.py V1 <<<")

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id   = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    rating      = Column(Integer, nullable=False)     # 1–5 stars
    comment     = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="reviews")
    reviewer = relationship("User")

    def __repr__(self):
        return f"<Review #{self.review_id} {self.rating}★ for Property #{self.property_id}>"