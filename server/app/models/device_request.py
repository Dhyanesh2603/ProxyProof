import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class DeviceRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class DeviceRequest(Base):
    __tablename__ = "device_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    old_device_uuid = Column(String(100), nullable=True)
    new_device_uuid = Column(String(100), nullable=False)
    new_device_name = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(DeviceRequestStatus), default=DeviceRequestStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="device_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
