from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.device import Device
from app.models.course import Course
from app.models.device_request import DeviceRequest, DeviceRequestStatus
from app.security.hashing import get_password_hash

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

    # 4. Device Change Request (Pending admin approval test)
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

    db.commit()
    print("Database successfully seeded with zero-stat baseline accounts:")
    print("  Organizer: prof.smith@university.edu / Admin@1234")
    print("  Student 1: alice@university.edu / Student@1234")
    print("  Student 2: bob@university.edu / Student@1234")
    print("  Courses: CS401, CS405")
    print("  Sessions & Attendance: 0 records (Fully Dynamic)")
