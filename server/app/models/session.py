import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class SessionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

class AttendanceSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_code = Column(String(32), unique=True, index=True, nullable=False)
    secret_key = Column(String(64), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60, nullable=False)
    rssi_threshold = Column(Integer, default=-75, nullable=False)  # dBm: default -75
    token_rotation_interval = Column(Integer, default=5, nullable=False) # seconds: default 5s
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    course = relationship("Course", back_populates="sessions")
    organizer = relationship("User", foreign_keys=[organizer_id])
    attendance_records = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")
    rotating_tokens = relationship("RotatingToken", back_populates="session", cascade="all, delete-orphan")
