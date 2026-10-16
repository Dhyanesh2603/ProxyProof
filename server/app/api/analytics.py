from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User, UserRole
from app.models.session import AttendanceSession, SessionStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.device import Device
from app.models.course import Course
from app.models.audit_log import AuditLog
from app.api.deps import get_current_user, get_current_organizer

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
def get_analytics_overview(
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    total_students = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar() or 0
    total_sessions = db.query(func.count(AttendanceSession.id)).scalar() or 0
    active_sessions = db.query(func.count(AttendanceSession.id)).filter(AttendanceSession.status == SessionStatus.ACTIVE).scalar() or 0
    
    total_present = db.query(func.count(Attendance.id)).filter(Attendance.status == AttendanceStatus.PRESENT).scalar() or 0
    total_late = db.query(func.count(Attendance.id)).filter(Attendance.status == AttendanceStatus.LATE).scalar() or 0
    total_rejected = db.query(func.count(Attendance.id)).filter(Attendance.status == AttendanceStatus.REJECTED).scalar() or 0
    
    total_attempts = total_present + total_late + total_rejected
    overall_attendance_rate = round(((total_present + total_late) / max(1, total_attempts)) * 100.0, 1) if total_attempts > 0 else 0.0
    
    registered_devices = db.query(func.count(Device.id)).filter(Device.is_active == True).scalar() or 0
    security_alerts = db.query(func.count(AuditLog.id)).filter(AuditLog.severity.in_(["WARNING", "CRITICAL"])).scalar() or 0

    return {
        "total_students": total_students,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_present": total_present,
        "total_late": total_late,
        "total_rejected": total_rejected,
        "overall_attendance_rate": overall_attendance_rate,
        "registered_devices": registered_devices,
        "security_alerts_count": security_alerts
    }

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 100,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    query = db.query(AuditLog)
    if severity:
        query = query.filter(AuditLog.severity == severity.upper())
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    out = []
    for log in logs:
        out.append({
            "id": log.id,
            "event_type": log.event_type,
            "severity": log.severity,
            "user_id": log.user_id,
            "user_name": log.user.full_name if log.user else "System",
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
    return out

@router.get("/reports")
def get_reports_summary(
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    # Aggregate attendance by course
    courses = db.query(Course).all()
    report = []
    for c in courses:
        sessions = db.query(AttendanceSession).filter(AttendanceSession.course_id == c.id).all()
        session_ids = [s.id for s in sessions]
        
        present = db.query(func.count(Attendance.id)).filter(
            Attendance.session_id.in_(session_ids),
            Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
        ).scalar() if session_ids else 0
        
        rejected = db.query(func.count(Attendance.id)).filter(
            Attendance.session_id.in_(session_ids),
            Attendance.status == AttendanceStatus.REJECTED
        ).scalar() if session_ids else 0
        
        report.append({
            "course_id": c.id,
            "course_code": c.code,
            "course_name": c.name,
            "section": c.section,
            "total_sessions": len(sessions),
            "successful_attendance": present,
            "rejected_attempts": rejected
        })
    return report
