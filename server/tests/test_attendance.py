import pytest
from app.services.token_service import TokenService
from app.models.session import AttendanceSession

def test_attendance_anti_proxy_pipeline(client, db_session):
    # 1. Login as Organizer to get active session
    org_login = client.post("/api/v1/auth/login", json={
        "email": "prof.smith@university.edu",
        "password": "Admin@1234"
    })
    org_token = org_login.json()["access_token"]
    org_headers = {"Authorization": f"Bearer {org_token}"}

    # Fetch active session
    sessions_resp = client.get("/api/v1/sessions", headers=org_headers)
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    active_session = next(s for s in sessions if s["status"] == "ACTIVE")
    session_id = active_session["id"]

    # 2. Get current rotating token from session
    token_resp = client.get(f"/api/v1/sessions/{session_id}/token", headers=org_headers)
    assert token_resp.status_code == 200
    current_token = token_resp.json()["token"]

    # 3. Login as student Diana (who has not yet marked attendance)
    stu_login = client.post("/api/v1/auth/login", json={
        "email": "diana@university.edu",
        "password": "Student@1234"
    })
    assert stu_login.status_code == 200
    diana_token = stu_login.json()["access_token"]
    diana_headers = {"Authorization": f"Bearer {diana_token}"}

    # Check Diana's registered device
    dev_resp = client.get("/api/v1/devices/my-device", headers=diana_headers)
    assert dev_resp.status_code == 200
    diana_device = dev_resp.json()["device"]
    diana_uuid = diana_device["device_uuid"]

    # TEST A: Valid Submission -> Should succeed (PRESENT)
    mark_resp = client.post("/api/v1/attendance/mark", json={
        "session_id": session_id,
        "token": current_token,
        "device_uuid": diana_uuid,
        "rssi": -65  # Strong indoor signal
    }, headers=diana_headers)
    assert mark_resp.status_code == 200
    mark_data = mark_resp.json()
    assert mark_data["success"] is True
    assert mark_data["status"] == "PRESENT"

    # TEST B: Duplicate Attempt -> Should be rejected
    dup_resp = client.post("/api/v1/attendance/mark", json={
        "session_id": session_id,
        "token": current_token,
        "device_uuid": diana_uuid,
        "rssi": -65
    }, headers=diana_headers)
    assert dup_resp.status_code == 200
    dup_data = dup_resp.json()
    assert dup_data["success"] is False
    assert "already" in dup_data["message"].lower()

def test_attendance_rejection_scenarios(client, db_session):
    # Register a fresh student with a device
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "fresh.student@university.edu",
        "password": "Student@1234",
        "full_name": "Fresh Student",
        "role": "STUDENT",
        "student_id": "CS2026-777"
    })
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register phone device
    client.post("/api/v1/devices/register", json={
        "device_uuid": "DEV-UUID-FRESH-PHONE",
        "device_name": "Fresh Phone 1"
    }, headers=headers)

    session = db_session.query(AttendanceSession).filter(AttendanceSession.status == "ACTIVE").first()
    session_id = session.id
    token_data = TokenService.get_or_create_active_token(db_session, session)
    valid_token = token_data["token"]

    # 1. Device mismatch check (Anti-spoofing)
    spoof_resp = client.post("/api/v1/attendance/mark", json={
        "session_id": session_id,
        "token": valid_token,
        "device_uuid": "ROGUE-EMULATOR-UUID-999",
        "rssi": -60
    }, headers=headers)
    assert spoof_resp.status_code == 200
    assert spoof_resp.json()["success"] is False
    assert "device mismatch" in spoof_resp.json()["message"].lower()

    # 2. Out-of-bounds RSSI check (Student outside classroom)
    weak_rssi_resp = client.post("/api/v1/attendance/mark", json={
        "session_id": session_id,
        "token": valid_token,
        "device_uuid": "DEV-UUID-FRESH-PHONE",
        "rssi": -88 # Very weak signal, e.g. downstairs or parking lot
    }, headers=headers)
    assert weak_rssi_resp.status_code == 200
    assert weak_rssi_resp.json()["success"] is False
    assert "weak" in weak_rssi_resp.json()["message"].lower()

    # 3. Expired/Fake Token check
    fake_token_resp = client.post("/api/v1/attendance/mark", json={
        "session_id": session_id,
        "token": "deadbeefcafebabe",
        "device_uuid": "DEV-UUID-FRESH-PHONE",
        "rssi": -60
    }, headers=headers)
    assert fake_token_resp.status_code == 200
    assert fake_token_resp.json()["success"] is False
    assert "token" in fake_token_resp.json()["message"].lower()
