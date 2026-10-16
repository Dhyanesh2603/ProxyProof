def test_register_and_login_flow(client):
    # Register student
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "sam.taylor@university.edu",
        "password": "SecurePassword@123",
        "full_name": "Sam Taylor",
        "role": "STUDENT",
        "student_id": "CS2026-999"
    })
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "sam.taylor@university.edu"

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "sam.taylor@university.edu",
        "password": "SecurePassword@123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token

    # Check /auth/me
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "sam.taylor@university.edu"

def test_login_invalid_password(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "prof.smith@university.edu",
        "password": "WrongPassword999"
    })
    assert resp.status_code == 401
    assert "detail" in resp.json()
