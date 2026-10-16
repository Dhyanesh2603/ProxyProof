import secrets
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.session import AttendanceSession, SessionStatus
from app.models.course import Course
from app.security.crypto_tokens import generate_session_secret
from app.repositories.session_repo import SessionRepository
from app.repositories.attendance_repo import AttendanceRepository
from app.websocket.manager import ws_manager
from app.services.anomaly_service import AnomalyService
from app.utils.time import utcnow, normalize_compare

class SessionService:
    @staticmethod
    def create_session(
        db: Session,
        organizer_id: int,
        course_id: int,
        duration_minutes: int = 60,
        rssi_threshold: int = -75,
        token_rotation_interval: int = 5
    ) -> AttendanceSession:
        repo = SessionRepository(db)
        session_code = f"SES-{secrets.randbelow(90000) + 10000}"
        secret_key = generate_session_secret()
        
        session = AttendanceSession(
            course_id=course_id,
            organizer_id=organizer_id,
            session_code=session_code,
            secret_key=secret_key,
            status=SessionStatus.SCHEDULED,
            duration_minutes=duration_minutes,
            rssi_threshold=rssi_threshold,
            token_rotation_interval=token_rotation_interval
        )
        created = repo.create(session)
        
        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="SESSION_CREATED",
            user_id=organizer_id,
            details={"session_id": created.id, "session_code": session_code},
            severity="INFO"
        )
        return created

    @staticmethod
    async def start_session(db: Session, session_id: int, organizer_id: int) -> AttendanceSession:
        repo = SessionRepository(db)
        session = repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.organizer_id != organizer_id:
            raise PermissionError("Only the session creator can start this session")
            
        session.status = SessionStatus.ACTIVE
        session.started_at = utcnow()
        repo.update(session)

        # Broadcast live status update
        await ws_manager.broadcast_session(session_id, {
            "type": "SESSION_STARTED",
            "session_id": session_id,
            "status": session.status.value,
            "started_at": session.started_at.isoformat()
        })
        
        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="SESSION_STARTED",
            user_id=organizer_id,
            details={"session_id": session_id, "session_code": session.session_code},
            severity="INFO"
        )
        return session

    @staticmethod
    async def end_session(db: Session, session_id: int, organizer_id: int) -> AttendanceSession:
        repo = SessionRepository(db)
        session = repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.organizer_id != organizer_id:
            raise PermissionError("Only the session creator can end this session")
            
        session.status = SessionStatus.ENDED
        session.ended_at = utcnow()
        repo.update(session)

        await ws_manager.broadcast_session(session_id, {
            "type": "SESSION_ENDED",
            "session_id": session_id,
            "status": session.status.value,
            "ended_at": session.ended_at.isoformat()
        })

        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="SESSION_ENDED",
            user_id=organizer_id,
            details={"session_id": session_id},
            severity="INFO"
        )
        return session

    @staticmethod
    def get_session_stats(db: Session, session_id: int) -> Dict[str, Any]:
        repo = SessionRepository(db)
        att_repo = AttendanceRepository(db)
        session = repo.get_by_id(session_id)
        if not session:
            return {}
        stats = att_repo.count_session_stats(session_id)
        
        # Calculate time remaining
        remaining_seconds = 0
        if session.status == SessionStatus.ACTIVE and session.started_at:
            c_now, c_start = normalize_compare(utcnow(), session.started_at)
            elapsed = (c_now - c_start).total_seconds()
            total_duration_sec = session.duration_minutes * 60
            remaining_seconds = max(0, int(total_duration_sec - elapsed))

        return {
            "session_id": session.id,
            "session_code": session.session_code,
            "status": session.status.value,
            "duration_minutes": session.duration_minutes,
            "rssi_threshold": session.rssi_threshold,
            "remaining_seconds": remaining_seconds,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "stats": stats
        }
