from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Device(Base):
    """
    Strict 1-to-1 binding between a Student User and their physical mobile phone hardware UUID.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    device_uuid = Column(String(100), unique=True, nullable=False, index=True)
    device_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    registered_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="device")
