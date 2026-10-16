import csv
import io
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.session import AttendanceSession
from app.models.course import Course
from app.models.user import User

class ExportService:
    @staticmethod
    def export_attendance_csv(
        db: Session,
        session_id: Optional[int] = None,
        course_id: Optional[int] = None,
        date_str: Optional[str] = None
    ) -> str:
        """
        Generates CSV export string from attendance records.
        Columns: Session Code, Course Code, Course Name, Section, Student ID, Student Name, Status, RSSI (dBm), Device UUID, Timestamp
        """
        query = db.query(
            Attendance, AttendanceSession, Course, User
        ).join(
            AttendanceSession, Attendance.session_id == AttendanceSession.id
        ).join(
            Course, AttendanceSession.course_id == Course.id
        ).join(
            User, Attendance.student_id == User.id
        )

        if session_id:
            query = query.filter(Attendance.session_id == session_id)
        if course_id:
            query = query.filter(AttendanceSession.course_id == course_id)

        records = query.order_by(Attendance.marked_at.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Attendance ID",
            "Session Code",
            "Course Code",
            "Course Name",
            "Section",
            "Student ID",
            "Student Name",
            "Status",
            "Rejection Reason",
            "RSSI (dBm)",
            "Device UUID",
            "Timestamp"
        ])

        for att, sess, crs, stu in records:
            writer.writerow([
                att.id,
                sess.session_code,
                crs.code,
                crs.name,
                crs.section,
                stu.student_id or "N/A",
                stu.full_name,
                att.status.value,
                att.rejection_reason or "",
                att.rssi,
                att.device_uuid,
                att.marked_at.isoformat() if att.marked_at else ""
            ])

        return output.getvalue()
