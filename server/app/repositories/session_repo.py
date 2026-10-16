from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.session import AttendanceSession, SessionStatus
from app.repositories.base import BaseRepository

class SessionRepository(BaseRepository[AttendanceSession]):
    def __init__(self, db: Session):
        super().__init__(AttendanceSession, db)

    def get_by_code(self, session_code: str) -> Optional[AttendanceSession]:
        return self.db.query(AttendanceSession).filter(AttendanceSession.session_code == session_code.strip()).first()

    def get_active_sessions(self) -> List[AttendanceSession]:
        return self.db.query(AttendanceSession).filter(AttendanceSession.status == SessionStatus.ACTIVE).all()

    def get_by_organizer(self, organizer_id: int) -> List[AttendanceSession]:
        return self.db.query(AttendanceSession).filter(AttendanceSession.organizer_id == organizer_id).order_by(AttendanceSession.created_at.desc()).all()
