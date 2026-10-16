import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    LATE = "LATE"
    REJECTED = "REJECTED"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    device_uuid = Column(String(100), nullable=False)
    token_used = Column(String(64), nullable=False)
    rssi = Column(Integer, nullable=False)  # dBm, e.g. -65
    status = Column(Enum(AttendanceStatus), nullable=False, index=True)
    rejection_reason = Column(String(255), nullable=True)
    window_index = Column(Integer, nullable=True)
    marked_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")
    device = relationship("Device")
