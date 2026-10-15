# ProxyProof REST API & WebSocket Specification

All REST endpoints are prefixed with `/api/v1`.

## 1. Authentication (`/api/v1/auth`)

### `POST /auth/register`
Register a new organizer or student account.
- **Request Body**:
  ```json
  {
    "email": "student@university.edu",
    "password": "Password@123",
    "full_name": "Student Name",
    "role": "STUDENT",
    "student_id": "CS2026-042"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": 1, "email": "...", "role": "STUDENT" }
  }
  ```

### `POST /auth/login`
Authenticate with email and password.
- **Request Body**:
  ```json
  { "email": "prof.smith@university.edu", "password": "Admin@1234" }
  ```

### `GET /auth/me`
Retrieve currently authenticated user profile. Requires `Bearer <JWT>`.

---

## 2. Sessions (`/api/v1/sessions`)

### `POST /sessions` *(Organizer Only)*
Create a new attendance session.
- **Request Body**:
  ```json
  {
    "course_id": 1,
    "duration_minutes": 60,
    "rssi_threshold": -75,
    "token_rotation_interval": 5
  }
  ```

### `GET /sessions`
List all sessions (filtered by instructor for organizers).

### `GET /sessions/{id}`
Retrieve session metadata and real-time attendance counts.

### `POST /sessions/{id}/start` *(Organizer Only)*
Activate session and initiate BLE broadcasting window.

### `POST /sessions/{id}/end` *(Organizer Only)*
Terminate session and invalidate all active tokens.

### `GET /sessions/{id}/token`
Retrieve the current rotating token, window index, and packed 26-byte BLE frame in hex.

---

## 3. Attendance (`/api/v1/attendance`)

### `POST /attendance/mark` *(Student Only)*
Submit received BLE token and hardware UUID for proximity verification.
- **Request Body**:
  ```json
  {
    "session_id": 1,
    "token": "e3b0c44298fc1c14",
    "device_uuid": "DEV-UUID-ALICE-15PRO",
    "rssi": -65
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "status": "PRESENT",
    "marked_at": "2026-10-16T12:00:00Z",
    "message": "Attendance successfully marked as PRESENT."
  }
  ```

### `GET /attendance/history`
Student past attendance records with overall percentage or organizer full class history.

### `GET /attendance/live/{session_id}`
Live stream of attendees and stats for active session.

### `GET /attendance/export` *(Organizer Only)*
Stream CSV export of attendance records (`?session_id=1`).

---

## 4. Devices (`/api/v1/devices`)

### `POST /devices/register` *(Student Only)*
Bind physical mobile phone hardware UUID to student account.

### `GET /devices/my-device`
Check currently registered phone status.

### `POST /devices/change-request` *(Student Only)*
Submit device migration request with student justification.

### `GET /devices/requests` *(Organizer Only)*
List pending and past device migration requests.

### `PUT /devices/approve/{request_id}` *(Organizer Only)*
Approve or reject device migration request.

---

## 5. WebSockets (`/ws`)

### `/ws/sessions/{session_id}`
Real-time session updates. Pushes events:
- `ATTENDANCE_MARKED`
- `ATTENDANCE_REJECTED`
- `SESSION_STARTED`
- `SESSION_ENDED`

### `/ws/events`
Global organizer channel for security alerts and device change notifications.
