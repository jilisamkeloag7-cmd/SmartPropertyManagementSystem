
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from Models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "Administrator"
    MANAGER = "Property Manager"
    OWNER = "Owner"
    TENANT = "Tenant"


class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    id_number     = Column(String(20), unique=True, nullable=False)
    name          = Column(String(100), nullable=False)
    email         = Column(String(120), unique=True, nullable=False)
    phone         = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum(UserRole), nullable=False, default=UserRole.TENANT)
    status        = Column(String(20), default="Active")
    created_at    = Column(DateTime, default=datetime.utcnow)

    security_question    = Column(String(200), nullable=True)
    security_answer_hash = Column(String(255), nullable=True)

    # --- Profile picture (filename only; full path resolved at runtime)
    profile_image = Column(String(255), nullable=True)

    ownerships      = relationship("Ownership", back_populates="owner", cascade="all, delete-orphan")
    leases          = relationship("Lease", back_populates="tenant", cascade="all, delete-orphan")
    notifications   = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    preferences     = relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan")
    maintenance     = relationship("MaintenanceRequest", back_populates="submitter")

    def __repr__(self):
        return f"<User {self.name} ({self.role.value})>"
