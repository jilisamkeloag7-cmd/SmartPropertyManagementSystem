
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from Models.base import Base


class PropertyImage(Base):
    __tablename__ = "property_images"

    image_id    = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"), nullable=False)
    filename    = Column(String(255), nullable=False)   # just the filename, not full path
    order_index = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="images")

    def __repr__(self):
        return f"<PropertyImage #{self.image_id} for Property #{self.property_id}>"
