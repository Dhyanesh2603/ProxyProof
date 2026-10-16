import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import AttendanceSession, SessionStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.device import Device
from app.repositories.attendance_repo import AttendanceRepository
from app.repositories.device_repo import DeviceRepository
from app.services.token_service import TokenService
from app.services.anomaly_service import AnomalyService
from app.services.redis_cache import cache
from app.websocket.manager import ws_manager
from app.config import settings
from app.utils.time import utcnow, normalize_compare

class AttendanceService:
    @staticmethod
    async def process_attendance(
        db: Session,
        student: User,
        session_id: int,
        token: str,
        device_uuid: str,
        rssi: int,
        client_ip: str = "127.0.0.1"
    ) -> Tuple[bool, Attendance, str]:
        """
        Executes the 8-Step Anti-Proxy Verification Pipeline.
        Returns: (success: bool, record: Attendance, message: str)
        """
        attendance_repo = AttendanceRepository(db)
        device_repo = DeviceRepository(db)

        # Rate Limit / Anomaly Check
        if AnomalyService.check_rate_limit(student.id, window_seconds=5, max_attempts=5):
            rejection_reason = "EXCESSIVE_RATE_LIMIT_EXCEEDED"
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="SUSPICIOUS_RAPID_ATTENDANCE",
                user_id=student.id,
                details={"reason": rejection_reason, "device_uuid": device_uuid, "rssi": rssi},
                severity="CRITICAL",
                ip_address=client_ip
            )
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=None,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            await AttendanceService._broadcast_event(db, session_id, "ATTENDANCE_REJECTED", rec, student)
            return False, rec, "Excessive attempts detected. Flagged for suspicious proxy activity."

        # Step 1: Verify Student has a bound, active device
        active_device = device_repo.get_by_user_id(student.id)
        if not active_device:
            rejection_reason = "NO_DEVICE_REGISTERED"
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=None,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            await AttendanceService._broadcast_event(db, session_id, "ATTENDANCE_REJECTED", rec, student)
            return False, rec, "No device registered for student. Please register your phone first."

        # Step 2: Verify Device Hardware Binding (Anti-Device Spoofing)
        if active_device.device_uuid.strip().lower() != device_uuid.strip().lower():
            rejection_reason = "DEVICE_HARDWARE_MISMATCH"
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="UNAUTHORIZED_DEVICE_SPOOF_ATTEMPT",
                user_id=student.id,
                details={
                    "registered_uuid": active_device.device_uuid,
                    "submitted_uuid": device_uuid,
                    "session_id": session_id
                },
                severity="CRITICAL",
                ip_address=client_ip
            )
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=active_device.id,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            await AttendanceService._broadcast_event(db, session_id, "ATTENDANCE_REJECTED", rec, student)
            return False, rec, "Device mismatch. Attendance can only be marked from your registered phone."

        # Step 3: Verify Session Exists & Is ACTIVE
        session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
        if not session or session.status != SessionStatus.ACTIVE:
            rejection_reason = "SESSION_NOT_ACTIVE"
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=active_device.id,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            return False, rec, "Attendance session is not currently active."

        # Step 4: Verify Session Expiry / Time Window
        now_dt = utcnow()
        if session.started_at:
            max_end = session.started_at + timedelta(minutes=session.duration_minutes)
            c_now, c_max = normalize_compare(now_dt, max_end)
            if c_now > c_max:
                rejection_reason = "SESSION_TIME_EXPIRED"
                rec = Attendance(
                    session_id=session_id,
                    student_id=student.id,
                    device_id=active_device.id,
                    device_uuid=device_uuid,
                    token_used=token,
                    rssi=rssi,
                    status=AttendanceStatus.REJECTED,
                    rejection_reason=rejection_reason
                )
                attendance_repo.create(rec)
                return False, rec, "Session duration has expired."

        # Step 5: Duplicate Prevention (One attendance per student per session)
        existing = attendance_repo.get_by_session_and_student(session.id, student.id)
        if existing:
            rejection_reason = "DUPLICATE_ATTENDANCE_ALREADY_MARKED"
            return False, existing, "Attendance has already been recorded for this session."

        # Step 6: Verify Proximity / RSSI Threshold
        threshold = session.rssi_threshold if session.rssi_threshold is not None else settings.DEFAULT_RSSI_THRESHOLD
        if rssi < threshold:
            rejection_reason = f"PROXIMITY_RSSI_TOO_WEAK ({rssi} dBm < threshold {threshold} dBm)"
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="OUT_OF_BOUNDS_RSSI_DETECTED",
                user_id=student.id,
                details={"rssi": rssi, "threshold": threshold, "session_id": session_id},
                severity="WARNING",
                ip_address=client_ip
            )
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=active_device.id,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            await AttendanceService._broadcast_event(db, session_id, "ATTENDANCE_REJECTED", rec, student)
            return False, rec, f"Signal too weak ({rssi} dBm). You must be physically inside the classroom."

        # Step 7: Cryptographic Rotating Token Verification (HMAC + Grace Window)
        is_valid_token, token_info = TokenService.validate_token(db, session, token)
        if not is_valid_token:
            rejection_reason = "INVALID_OR_EXPIRED_ROTATING_TOKEN"
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="INVALID_ROTATING_TOKEN_SUBMISSION",
                user_id=student.id,
                details={"token_candidate": token, "session_id": session_id},
                severity="WARNING",
                ip_address=client_ip
            )
            rec = Attendance(
                session_id=session_id,
                student_id=student.id,
                device_id=active_device.id,
                device_uuid=device_uuid,
                token_used=token,
                rssi=rssi,
                status=AttendanceStatus.REJECTED,
                rejection_reason=rejection_reason
            )
            attendance_repo.create(rec)
            await AttendanceService._broadcast_event(db, session_id, "ATTENDANCE_REJECTED", rec, student)
            return False, rec, "Expired or invalid BLE token. Replay prevented."

        # Step 8: Determine PRESENT vs LATE status
        status = AttendanceStatus.PRESENT
        if session.started_at:
            c_now, c_start = normalize_compare(now_dt, session.started_at)
            elapsed_minutes = (c_now - c_start).total_seconds() / 60.0
            if elapsed_minutes > settings.ATTENDANCE_LATE_THRESHOLD_MINUTES:
                status = AttendanceStatus.LATE

        # ALL 8 CHECKS PASSED: Record Attendance
        attendance_record = Attendance(
            session_id=session.id,
            student_id=student.id,
            device_id=active_device.id,
            device_uuid=device_uuid,
            token_used=token,
            rssi=rssi,
            status=status,
            rejection_reason=None
        )
        attendance_repo.create(attendance_record)

        # Update Device last_used_at
        active_device.last_used_at = now_dt
        db.commit()

        # Audit Log Successful Verification
        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="ATTENDANCE_SUCCESSFULLY_VERIFIED",
            user_id=student.id,
            details={
                "session_id": session.id,
                "status": status.value,
                "rssi": rssi,
                "device_uuid": device_uuid
            },
            severity="INFO",
            ip_address=client_ip
        )

        # Broadcast real-time update to WebSocket dashboard
        await AttendanceService._broadcast_event(db, session.id, "ATTENDANCE_MARKED", attendance_record, student)

        return True, attendance_record, f"Attendance successfully marked as {status.value}."

    @staticmethod
    async def _broadcast_event(db: Session, session_id: int, event_type: str, record: Attendance, student: User):
        repo = AttendanceRepository(db)
        stats = repo.count_session_stats(session_id)
        
        event_payload = {
            "type": event_type,
            "session_id": session_id,
            "stats": stats,
            "record": {
                "id": record.id,
                "student_id": student.id,
                "student_name": student.full_name,
                "student_code": student.student_id or "N/A",
                "device_uuid": record.device_uuid,
                "rssi": record.rssi,
                "status": record.status.value,
                "rejection_reason": record.rejection_reason,
                "marked_at": record.marked_at.isoformat() if record.marked_at else None
            }
        }
        await ws_manager.broadcast_session(session_id, event_payload)
