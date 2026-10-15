from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.attendance import Attendance, AttendanceStatus
from app.repositories.base import BaseRepository

class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: Session):
        super().__init__(Attendance, db)

    def get_by_session_and_student(self, session_id: int, student_id: int) -> Optional[Attendance]:
        """Find any successful attendance marked for this student in this session."""
        return self.db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.student_id == student_id,
            Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
        ).first()

    def get_session_records(self, session_id: int) -> List[Attendance]:
        return self.db.query(Attendance).filter(
            Attendance.session_id == session_id
        ).order_by(Attendance.marked_at.desc()).all()

    def get_student_history(self, student_id: int) -> List[Attendance]:
        return self.db.query(Attendance).filter(
            Attendance.student_id == student_id
        ).order_by(Attendance.marked_at.desc()).all()

    def count_session_stats(self, session_id: int) -> dict:
        present_count = self.db.query(func.count(Attendance.id)).filter(
            Attendance.session_id == session_id,
            Attendance.status == AttendanceStatus.PRESENT
        ).scalar() or 0

        late_count = self.db.query(func.count(Attendance.id)).filter(
            Attendance.session_id == session_id,
            Attendance.status == AttendanceStatus.LATE
        ).scalar() or 0

        rejected_count = self.db.query(func.count(Attendance.id)).filter(
            Attendance.session_id == session_id,
            Attendance.status == AttendanceStatus.REJECTED
        ).scalar() or 0

        return {
            "present": present_count,
            "late": late_count,
            "rejected": rejected_count,
            "total_marked": present_count + late_count
        }
