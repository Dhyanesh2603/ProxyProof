from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.attendance import Attendance
from app.models.session import AttendanceSession
from app.api.deps import get_current_user, get_current_student, get_current_organizer
from app.services.attendance_service import AttendanceService
from app.services.export_service import ExportService
from app.repositories.attendance_repo import AttendanceRepository

router = APIRouter(prefix="/attendance", tags=["Attendance"])

class MarkAttendanceRequest(BaseModel):
    session_id: int
    token: str
    device_uuid: str
    rssi: int
    timestamp: Optional[float] = None

@router.post("/mark")
async def mark_attendance(
    req: MarkAttendanceRequest,
    request: Request,
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success, record, message = await AttendanceService.process_attendance(
        db=db,
        student=student,
        session_id=req.session_id,
        token=req.token,
        device_uuid=req.device_uuid,
        rssi=req.rssi,
        client_ip=client_ip
    )

    if not success:
        return {
            "success": False,
            "status": record.status.value,
            "rejection_reason": record.rejection_reason,
            "message": message
        }

    return {
        "success": True,
        "status": record.status.value,
        "marked_at": record.marked_at.isoformat() if record.marked_at else None,
        "message": message
    }

class ManualMarkRequest(BaseModel):
    session_id: int
    student_id: int
    status: str = "PRESENT"
    note: Optional[str] = "Manual mark by organizer"

@router.post("/manual")
async def manual_mark_attendance(
    req: ManualMarkRequest,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    try:
        from app.models.attendance import AttendanceStatus
        att_status = AttendanceStatus.PRESENT if req.status == "PRESENT" else AttendanceStatus.LATE
        rec = await AttendanceService.manual_mark(
            db=db,
            session_id=req.session_id,
            student_id=req.student_id,
            status=att_status,
            note=req.note or "Manual override"
        )
        return {
            "success": True,
            "id": rec.id,
            "status": rec.status.value,
            "marked_at": rec.marked_at.isoformat() if rec.marked_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{attendance_id}")
async def remove_attendance_record(
    attendance_id: int,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    success = await AttendanceService.remove_attendance(db, attendance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return {"success": True, "message": "Attendance record revoked"}

@router.get("/history")
def get_attendance_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    repo = AttendanceRepository(db)
    if user.role == UserRole.STUDENT:
        records = repo.get_student_history(user.id)
        # Calculate student percentage
        total_present = sum(1 for r in records if r.status.value in ["PRESENT", "LATE"])
        total_sessions = db.query(AttendanceSession).count()
        percentage = round((total_present / max(1, total_sessions)) * 100.0, 1) if total_sessions > 0 else 100.0
        
        items = []
        for r in records:
            items.append({
                "id": r.id,
                "session_id": r.session_id,
                "session_code": r.session.session_code if r.session else "N/A",
                "course_code": r.session.course.code if r.session and r.session.course else "N/A",
                "course_name": r.session.course.name if r.session and r.session.course else "N/A",
                "status": r.status.value,
                "rejection_reason": r.rejection_reason,
                "rssi": r.rssi,
                "marked_at": r.marked_at.isoformat() if r.marked_at else None
            })
        return {
            "percentage": percentage,
            "total_present": total_present,
            "total_attempts": len(records),
            "history": items
        }
    else:
        # Organizer view: all records
        records = db.query(Attendance).order_by(Attendance.marked_at.desc()).limit(200).all()
        items = []
        for r in records:
            items.append({
                "id": r.id,
                "session_id": r.session_id,
                "session_code": r.session.session_code if r.session else "N/A",
                "course_code": r.session.course.code if r.session and r.session.course else "N/A",
                "student_id": r.student_id,
                "student_name": r.student.full_name if r.student else "Unknown",
                "student_code": r.student.student_id if r.student else "N/A",
                "device_uuid": r.device_uuid,
                "status": r.status.value,
                "rejection_reason": r.rejection_reason,
                "rssi": r.rssi,
                "marked_at": r.marked_at.isoformat() if r.marked_at else None
            })
        return items

@router.get("/live/{session_id}")
def get_live_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    repo = AttendanceRepository(db)
    records = repo.get_session_records(session_id)
    stats = repo.count_session_stats(session_id)

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.full_name if r.student else "Unknown",
            "student_code": r.student.student_id if r.student else "N/A",
            "device_uuid": r.device_uuid,
            "rssi": r.rssi,
            "status": r.status.value,
            "rejection_reason": r.rejection_reason,
            "marked_at": r.marked_at.isoformat() if r.marked_at else None
        })

    return {
        "session_id": session_id,
        "stats": stats,
        "records": items
    }

@router.get("/export")
def export_csv(
    session_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    csv_data = ExportService.export_attendance_csv(db, session_id=session_id, course_id=course_id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=proxyproof_attendance_{session_id or 'all'}.csv"}
    )
