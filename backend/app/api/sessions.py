from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.session import AttendanceSession, SessionStatus
from app.api.deps import get_current_user, get_current_organizer
from app.services.session_service import SessionService
from app.services.token_service import TokenService

router = APIRouter(prefix="/sessions", tags=["Sessions"])

class CreateSessionRequest(BaseModel):
    course_id: int
    duration_minutes: int = 60
    rssi_threshold: int = -75
    token_rotation_interval: int = 5

class CreateCourseRequest(BaseModel):
    code: str
    name: str
    section: str = "A"

@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    req: CreateSessionRequest,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    course = db.query(Course).filter(Course.id == req.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    session = SessionService.create_session(
        db=db,
        organizer_id=organizer.id,
        course_id=req.course_id,
        duration_minutes=req.duration_minutes,
        rssi_threshold=req.rssi_threshold,
        token_rotation_interval=req.token_rotation_interval
    )
    return {
        "id": session.id,
        "session_code": session.session_code,
        "course_id": session.course_id,
        "course_code": course.code,
        "course_name": course.name,
        "section": course.section,
        "status": session.status.value,
        "duration_minutes": session.duration_minutes,
        "rssi_threshold": session.rssi_threshold,
        "token_rotation_interval": session.token_rotation_interval,
        "created_at": session.created_at.isoformat() if session.created_at else None
    }

@router.get("")
def list_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(AttendanceSession, Course).join(Course, AttendanceSession.course_id == Course.id)
    if user.role.value == "ORGANIZER":
        query = query.filter(AttendanceSession.organizer_id == user.id)
        
    results = query.order_by(AttendanceSession.created_at.desc()).all()
    out = []
    for sess, crs in results:
        out.append({
            "id": sess.id,
            "session_code": sess.session_code,
            "course_id": sess.course_id,
            "course_code": crs.code,
            "course_name": crs.name,
            "section": crs.section,
            "status": sess.status.value,
            "duration_minutes": sess.duration_minutes,
            "rssi_threshold": sess.rssi_threshold,
            "started_at": sess.started_at.isoformat() if sess.started_at else None,
            "ended_at": sess.ended_at.isoformat() if sess.ended_at else None,
            "created_at": sess.created_at.isoformat() if sess.created_at else None
        })
    return out

@router.get("/{session_id}")
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    stats = SessionService.get_session_stats(db, session_id)
    course = db.query(Course).filter(Course.id == session.course_id).first()
    return {
        **stats,
        "course_code": course.code if course else "",
        "course_name": course.name if course else "",
        "section": course.section if course else ""
    }

@router.post("/{session_id}/start")
async def start_session(
    session_id: int,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    try:
        session = await SessionService.start_session(db, session_id, organizer.id)
        return {"message": "Session started", "status": session.status.value, "started_at": session.started_at.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    try:
        session = await SessionService.end_session(db, session_id, organizer.id)
        return {"message": "Session ended", "status": session.status.value, "ended_at": session.ended_at.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/{session_id}/token")
def get_current_token(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
        
    token_data = TokenService.get_or_create_active_token(db, session)
    return token_data

# Course endpoints for convenience
@router.post("/courses/create", status_code=status.HTTP_201_CREATED)
def create_course(
    req: CreateCourseRequest,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    course = Course(
        code=req.code.upper().strip(),
        name=req.name.strip(),
        section=req.section.upper().strip(),
        created_by=organizer.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return {
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "section": course.section
    }

@router.get("/courses/list")
def list_courses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    courses = db.query(Course).all()
    return [{"id": c.id, "code": c.code, "name": c.name, "section": c.section} for c in courses]
