import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    ORGANIZER = "ORGANIZER"
    STUDENT = "STUDENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    device = relationship("Device", back_populates="user", uselist=False, cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student")
    device_requests = relationship("DeviceRequest", back_populates="user", foreign_keys="DeviceRequest.user_id")
    audit_logs = relationship("AuditLog", back_populates="user")
