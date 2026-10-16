from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.device import Device
from app.models.course import Course
from app.models.session import AttendanceSession, SessionStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.device_request import DeviceRequest, DeviceRequestStatus
from app.models.audit_log import AuditLog
from app.security.hashing import get_password_hash
from app.security.crypto_tokens import generate_session_secret

def utcnow():
    return datetime.now(timezone.utc)

def seed_database(db: Session):
    # Check if already seeded
    if db.query(User).first():
        return

    print("Seeding ProxyProof database with initial enterprise demo data...")

    # 1. Organizer
    prof = User(
        email="prof.smith@university.edu",
        hashed_password=get_password_hash("Admin@1234"),
        full_name="Prof. Harrison Smith",
        role=UserRole.ORGANIZER,
        student_id=None,
        is_active=True
    )
    db.add(prof)
    db.flush()

    # 2. Courses
    course_cs401 = Course(
        code="CS401",
        name="Distributed Systems & Cloud Architecture",
        section="A",
        created_by=prof.id
    )
    course_cs405 = Course(
        code="CS405",
        name="Network Security & Applied Cryptography",
        section="B",
        created_by=prof.id
    )
    db.add_all([course_cs401, course_cs405])
    db.flush()

    # 3. Students & Devices
    students_data = [
        ("alice@university.edu", "Alice Zhang", "CS2026-001", "iPhone 15 Pro", "DEV-UUID-ALICE-15PRO"),
        ("bob@university.edu", "Bob Miller", "CS2026-002", "Google Pixel 8", "DEV-UUID-BOB-PIXEL8"),
        ("charlie@university.edu", "Charlie Patel", "CS2026-003", "Samsung Galaxy S24", "DEV-UUID-CHARLIE-S24"),
        ("diana@university.edu", "Diana Rossi", "CS2026-004", "OnePlus 12", "DEV-UUID-DIANA-OP12"),
        ("evan@university.edu", "Evan Wright", "CS2026-005", "iPhone 14", "DEV-UUID-EVAN-IP14"),
    ]

    student_objs = []
    device_objs = []
    for email, name, sid, dev_name, dev_uuid in students_data:
        stu = User(
            email=email,
            hashed_password=get_password_hash("Student@1234"),
            full_name=name,
            role=UserRole.STUDENT,
            student_id=sid,
            is_active=True
        )
        db.add(stu)
        db.flush()
        student_objs.append(stu)

        dev = Device(
            user_id=stu.id,
            device_uuid=dev_uuid,
            device_name=dev_name,
            is_active=True,
            last_used_at=utcnow()
        )
        db.add(dev)
        device_objs.append(dev)

    db.flush()

    # 4. Sessions
    # Active Session in CS401
    active_session = AttendanceSession(
        course_id=course_cs401.id,
        organizer_id=prof.id,
        session_code="SES-40101",
        secret_key=generate_session_secret(),
        status=SessionStatus.ACTIVE,
        duration_minutes=60,
        rssi_threshold=-75,
        token_rotation_interval=5,
        started_at=utcnow() - timedelta(minutes=5)
    )
    # Past Completed Session in CS405
    past_session = AttendanceSession(
        course_id=course_cs405.id,
        organizer_id=prof.id,
        session_code="SES-40599",
        secret_key=generate_session_secret(),
        status=SessionStatus.ENDED,
        duration_minutes=45,
        rssi_threshold=-75,
        token_rotation_interval=5,
        started_at=utcnow() - timedelta(days=2, hours=1),
        ended_at=utcnow() - timedelta(days=2, minutes=15)
    )
    db.add_all([active_session, past_session])
    db.flush()

    # 5. Attendance records
    # Alice and Bob arrived in active session
    att_alice = Attendance(
        session_id=active_session.id,
        student_id=student_objs[0].id,
        device_id=device_objs[0].id,
        device_uuid=device_objs[0].device_uuid,
        token_used="e3b0c44298fc1c14",
        rssi=-62,
        status=AttendanceStatus.PRESENT,
        marked_at=utcnow() - timedelta(minutes=3)
    )
    att_bob = Attendance(
        session_id=active_session.id,
        student_id=student_objs[1].id,
        device_id=device_objs[1].id,
        device_uuid=device_objs[1].device_uuid,
        token_used="9f86d081884c7d65",
        rssi=-69,
        status=AttendanceStatus.PRESENT,
        marked_at=utcnow() - timedelta(minutes=1)
    )
    # Rejected attempt: proxy attempt from Charlie with weak RSSI
    att_charlie_weak = Attendance(
        session_id=active_session.id,
        student_id=student_objs[2].id,
        device_id=device_objs[2].id,
        device_uuid=device_objs[2].device_uuid,
        token_used="5e884898da280471",
        rssi=-84,
        status=AttendanceStatus.REJECTED,
        rejection_reason="PROXIMITY_RSSI_TOO_WEAK (-84 dBm < threshold -75 dBm)",
        marked_at=utcnow() - timedelta(minutes=2)
    )
    db.add_all([att_alice, att_bob, att_charlie_weak])

    # 6. Device Change Request
    # Evan requested changing from old iPhone 14 to new iPad / Galaxy
    dev_req = DeviceRequest(
        user_id=student_objs[4].id,
        old_device_uuid=device_objs[4].device_uuid,
        new_device_uuid="DEV-UUID-EVAN-IPADPRO",
        new_device_name="iPad Pro M4",
        reason="Screen damaged on primary phone; using authorized university tablet for lectures.",
        status=DeviceRequestStatus.PENDING
    )
    db.add(dev_req)

    # 7. Audit Logs
    audit1 = AuditLog(
        event_type="SESSION_STARTED",
        severity="INFO",
        user_id=prof.id,
        details='{"session_id": 1, "session_code": "SES-40101", "course": "CS401"}',
        ip_address="192.168.1.10"
    )
    audit2 = AuditLog(
        event_type="OUT_OF_BOUNDS_RSSI_DETECTED",
        severity="WARNING",
        user_id=student_objs[2].id,
        details='{"rssi": -84, "threshold": -75, "session_id": 1}',
        ip_address="192.168.1.105"
    )
    db.add_all([audit1, audit2])

    db.commit()
    print("Database successfully seeded with demo accounts:")
    print("  Organizer: prof.smith@university.edu / Admin@1234")
    print("  Student 1: alice@university.edu / Student@1234")
    print("  Student 2: bob@university.edu / Student@1234")
