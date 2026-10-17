# ProxyProof – BLE-Based Smart Attendance System

> A secure, enterprise-grade Bluetooth Low Energy (BLE) attendance verification platform designed to guarantee physical student presence inside lecture halls through rotating cryptographic tokens, 1-to-1 hardware device binding, and server-side RF proximity validation.

[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Swagger UI](https://img.shields.io/badge/API_Docs-Swagger_UI-85EA2D?style=flat&logo=swagger&logoColor=black)](http://localhost:8005/docs)
[![ReDoc](https://img.shields.io/badge/API_Docs-ReDoc-blue?style=flat&logo=readme&logoColor=white)](http://localhost:8005/redoc)
[![API Specification](https://img.shields.io/badge/Spec-docs%2Fapi__spec.md-orange?style=flat&logo=markdown)](docs/api_spec.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

### 📌 Quick Links
- 📖 [Interactive API Documentation & Endpoints](#interactive-api-documentation--endpoints)
- 📐 [Architecture Overview](#architecture-overview)
- 🔄 [BLE Workflow & Attendance Lifecycle](#ble-workflow--attendance-lifecycle)
- 🗄️ [Entity-Relationship (ER) Diagram](#entity-relationship-er-diagram)
- 📁 [Folder Structure](#folder-structure)
- 🚀 [Quickstart & Local Setup](#quickstart--local-setup)
- 🐳 [Turnkey Docker Deployment](#turnkey-docker-deployment)
- 🧪 [Server Integration Test Suite](#3-run-server-integration-test-suite)
- 🛡️ [Anti-Proxy Security Guarantees](#anti-proxy-security-guarantees)
- 📚 [Private Developer Guide (Local)](file:///d:/vinno_app/documentation.html)

---

## Interactive API Documentation & Endpoints

ProxyProof provides fully interactive OpenAPI / Swagger specifications, ReDoc documentation, raw JSON schema, and real-time WebSocket feeds:

| Interface / Resource | Local Standalone (`:8005`) | Turnkey Docker (`:8000`) | Description |
| :--- | :--- | :--- | :--- |
| **Interactive Swagger UI** | [`http://localhost:8005/docs`](http://localhost:8005/docs) | [`http://localhost:8000/docs`](http://localhost:8000/docs) | Live browser-based OpenAPI explorer to test all endpoints with JWT Bearer auth |
| **ReDoc Documentation** | [`http://localhost:8005/redoc`](http://localhost:8005/redoc) | [`http://localhost:8000/redoc`](http://localhost:8000/redoc) | Responsive, clean visual technical specification and payload models |
| **OpenAPI Schema (JSON)** | [`http://localhost:8005/openapi.json`](http://localhost:8005/openapi.json) | [`http://localhost:8000/openapi.json`](http://localhost:8000/openapi.json) | Machine-readable OpenAPI 3.1.0 schema for Postman import and SDK generation |
| **In-Repo API Reference** | [`docs/api_spec.md`](docs/api_spec.md) | [`docs/api_spec.md`](docs/api_spec.md) | Comprehensive markdown documentation of payloads, status codes, and query params |
| **Session WebSocket** | `ws://localhost:8005/ws/sessions/{id}` | `ws://localhost:8000/ws/sessions/{id}` | Real-time session attendance stream (new attendees, rejections, status changes) |
| **Global Events WebSocket** | `ws://localhost:8005/ws/events` | `ws://localhost:8000/ws/events` | Organizer broadcast stream for security anomalies, audit events, and device alerts |

### REST API Endpoints Quick Reference

All endpoints are prefixed with `/api/v1` and protected with standard JWT tokens (`Authorization: Bearer <TOKEN>`).

#### 🔐 Authentication & Profile (`/api/v1/auth`)
| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public | Register new Organizer or Student account |
| `POST` | `/api/v1/auth/login` | Public | Authenticate with email/password and obtain JWT access token |
| `GET` | `/api/v1/auth/me` | Authenticated | Retrieve profile, role, student ID, and registered device metadata |

#### 📡 Attendance Sessions (`/api/v1/sessions`)
| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/sessions` | Organizer | Create session with course ID, duration, RSSI threshold, and rotation |
| `GET` | `/api/v1/sessions` | Authenticated | List all active and past sessions |
| `GET` | `/api/v1/sessions/{id}` | Authenticated | Retrieve session metadata and live attendee metrics |
| `POST` | `/api/v1/sessions/{id}/start` | Organizer | Activate session and start 5-second rotating HMAC-SHA256 token broadcaster |
| `POST` | `/api/v1/sessions/{id}/end` | Organizer | Conclude session and lock attendance records |
| `GET` | `/api/v1/sessions/{id}/token` | Authenticated | Get current rotating token, window index, and packed 26-byte BLE frame |

#### 🎯 Attendance & Verification Pipeline (`/api/v1/attendance`)
| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/attendance/mark` | Student / Organizer | Submit BLE token, hardware UUID & RSSI for 8-step anti-proxy verification |
| `GET` | `/api/v1/attendance/history` | Authenticated | Student personal attendance record & % or Organizer full class history |
| `GET` | `/api/v1/attendance/live/{session_id}` | Organizer | Live attendance stream and breakdown (PRESENT, LATE, REJECTED) |
| `POST` | `/api/v1/attendance/manual` | Organizer | Manually record or adjust student status with audit logging |
| `DELETE` | `/api/v1/attendance/{attendance_id}` | Organizer | Revoke or remove invalid attendance entry |
| `GET` | `/api/v1/attendance/export` | Organizer | Download attendance data as CSV (`?session_id=1`) |

#### 📱 Device Binding & Hardware Security (`/api/v1/devices`)
| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/devices/register` | Student | Bind permanent physical phone UUID to student account (1-to-1) |
| `GET` | `/api/v1/devices/my-device` | Student | Check current hardware registration status |
| `POST` | `/api/v1/devices/change-request` | Student | Request hardware migration with student justification |
| `GET` | `/api/v1/devices/requests` | Organizer | Review pending student hardware device migration requests |
| `PUT` | `/api/v1/devices/approve/{request_id}` | Organizer | Approve or reject device migration request |

#### 📊 Analytics & System Health (`/api/v1/analytics`, `/api/v1/health`)
| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/analytics` | Organizer | System metrics: student count, total sessions, present rate, device stats |
| `GET` | `/api/v1/analytics/audit-logs` | Organizer | Query security audit trail with severity filtering (`INFO`, `WARNING`, `CRITICAL`) |
| `GET` | `/api/v1/health` | Public | System health check (database connection, Redis cache status, uptime) |

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Classroom ["Physical Classroom Boundary (RSSI >= -75 dBm)"]
        OrganizerPhone["Organizer Phone / Beacon<br/>(BLE Broadcaster 0x5050)"]
        StudentPhone["Student Phone<br/>(Continuous BLE Scanner)"]
    end

    subgraph BackendInfrastructure ["ProxyProof Cloud Backend"]
        FastAPI["FastAPI REST & WebSocket Gateway"]
        AuthModule["JWT & RBAC Security Layer"]
        Pipeline["8-Step Anti-Proxy Verification Engine"]
        RedisCache["Redis In-Memory Cache<br/>(Sub-ms Replay Nonce & Token Lookup)"]
        PostgreSQL["PostgreSQL Database<br/>(Users, Sessions, Attendance, AuditLogs)"]
    end

    subgraph MonitoringConsole ["Organizer Web Console (React + Vite)"]
        Dashboard["Real-Time Live Monitor<br/>(Present, Late, Rejected, Beacon HUD)"]
        WSFeed["WebSocket Real-Time Event Stream"]
    end

    OrganizerPhone -- "Rotates HMAC Token every 5s" --> StudentPhone
    StudentPhone -- "POST /api/v1/attendance/mark<br/>(Token, Device UUID, RSSI)" --> FastAPI
    FastAPI --> AuthModule --> Pipeline
    Pipeline <--> RedisCache
    Pipeline --> PostgreSQL
    Pipeline -- "Push Live Event" --> WSFeed --> Dashboard
```

---

## BLE Workflow & Attendance Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Organizer as Organizer / Instructor
    actor Student as Student
    participant Mobile as Student App (Flutter)
    participant Server as ProxyProof Backend
    participant Dashboard as Live Web Console

    Organizer->>Server: POST /sessions/{id}/start
    Server-->>Organizer: Session Activated + SecretKey
    Organizer->>Organizer: Start BLE Advertising (0x5050, SessionID, Token)
    Note over Organizer: Token rotates every 5 seconds (HMAC-SHA256)

    Student->>Mobile: Enters classroom with app open
    Mobile->>Mobile: Scans BLE advertisement & measures RSSI (-62 dBm)
    Mobile->>Server: POST /attendance/mark (SessionID, Token, DeviceUUID, RSSI)
    
    rect rgb(20, 24, 20)
        Note over Server: 8-Step Anti-Proxy Verification
        Server->>Server: 1. Validate bound hardware Device UUID
        Server->>Server: 2. Verify Session is ACTIVE & within time window
        Server->>Server: 3. Verify RSSI >= -75 dBm threshold
        Server->>Server: 4. Verify HMAC token crypto & grace window
        Server->>Server: 5. Prevent duplicate submission
    end

    Server-->>Mobile: 200 OK (Status: PRESENT)
    Server--)Dashboard: WebSocket Event (ATTENDANCE_MARKED)
    Dashboard->>Dashboard: Live Table Updates Instantly
```

---

## Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ DEVICES : owns
    USERS ||--o{ SESSIONS : organizes
    USERS ||--o{ ATTENDANCE : marks
    USERS ||--o{ DEVICE_REQUESTS : requests
    USERS ||--o{ AUDIT_LOGS : triggers

    COURSES ||--o{ SESSIONS : has
    SESSIONS ||--o{ ATTENDANCE : contains
    SESSIONS ||--o{ ROTATING_TOKENS : generates

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role "ORGANIZER | STUDENT"
        string student_id UK
        boolean is_active
        datetime created_at
    }

    DEVICES {
        int id PK
        int user_id FK, UK
        string device_uuid UK
        string device_name
        boolean is_active
        datetime registered_at
        datetime last_used_at
    }

    COURSES {
        int id PK
        string code
        string name
        string section
        int created_by FK
        datetime created_at
    }

    SESSIONS {
        int id PK
        int course_id FK
        int organizer_id FK
        string session_code UK
        string secret_key
        string status "SCHEDULED | ACTIVE | ENDED"
        int duration_minutes
        int rssi_threshold
        int token_rotation_interval
        datetime started_at
        datetime ended_at
    }

    ATTENDANCE {
        int id PK
        int session_id FK
        int student_id FK
        int device_id FK
        string device_uuid
        string token_used
        int rssi
        string status "PRESENT | LATE | REJECTED"
        string rejection_reason
        datetime marked_at
    }

    DEVICE_REQUESTS {
        int id PK
        int user_id FK
        string old_device_uuid
        string new_device_uuid
        string new_device_name
        string reason
        string status "PENDING | APPROVED | REJECTED"
        int reviewed_by FK
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        string event_type
        string severity "INFO | WARNING | CRITICAL"
        int user_id FK
        text details
        string ip_address
        datetime created_at
    }
```

---

## Folder Structure

```
d:\vinno_app\
├── server/
│   ├── app/
│   │   ├── api/            # REST Endpoints (auth, sessions, attendance, devices, analytics)
│   │   ├── services/       # Business Logic (attendance_service, token_service, anomaly_service)
│   │   ├── repositories/   # Base and entity database repositories
│   │   ├── models/         # SQLAlchemy models (User, Device, Session, Attendance, AuditLog)
│   │   ├── security/       # JWT tokens, bcrypt hashing, HMAC rotating crypto
│   │   ├── websocket/      # Real-time WebSocket connection manager
│   │   ├── middleware/     # Access logging and rate limiter
│   │   ├── utils/          # Seed data and datetime normalizers
│   │   ├── config.py       # Pydantic environment configuration
│   │   ├── database.py     # SQLAlchemy engine and session
│   │   └── main.py         # FastAPI application entrypoint
│   ├── tests/              # Pytest test suite (7 comprehensive integration tests)
│   ├── Dockerfile
│   └── requirements.txt
├── client/
│   ├── src/
│   │   ├── pages/          # LiveSession, Sessions, AttendanceHistory, DeviceApproval, AuditLog, Analytics, Login
│   │   ├── components/     # TokenBeaconSimulator, Navbar, StatsCard, Modal, Badge
│   │   ├── services/       # API client and WebSocket client
│   │   ├── hooks/          # useAuth hook
│   │   ├── types/          # TypeScript interface definitions
│   │   ├── App.tsx         # Tab router and global layout
│   │   └── main.tsx        # React entrypoint with TanStack QueryClient
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── mobile/
│   ├── lib/
│   │   ├── screens/        # StudentHomeScreen, OrganizerSessionScreen, DeviceRegistration, Login, Register
│   │   ├── services/       # ble_scanner_service, ble_advertiser_service, device_info_service
│   │   ├── providers/      # Riverpod state notifiers
│   │   ├── widgets/        # ble_radar, status_badge, attendance_card, enterprise_card
│   │   ├── models/         # ble_packet (26-byte binary decoder), user, session, attendance
│   │   └── main.dart
│   ├── pubspec.yaml
│   └── README.md
├── scripts/
│   ├── demo_walkthrough.py # Instant 5-scenario anti-proxy test harness
│   └── load_test.py        # High-concurrency stress benchmark (100, 500, 1000 students)
├── docker/
│   ├── docker-compose.yml  # Turnkey multi-container stack (Server, Client, Postgres, Redis)
│   └── .env.example
├── docs/
│   ├── ble_protocol.md     # BLE 26-byte frame specification and RF path loss model
│   ├── security_model.md   # Threat model and 8-point anti-proxy pipeline
│   └── api_spec.md         # Complete REST API reference
├── ARCHITECTURE.html       # Standalone interactive developer & interview guide
└── README.md
```

---

## Quickstart & Local Setup

### 1. Run Server Standalone (Python 3.13)
```bash
cd server
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```
The database will automatically initialize SQLite `proxyproof.db` and seed demo users:
- **Organizer**: `prof.smith@university.edu` / `Admin@1234`
- **Student 1**: `alice@university.edu` / `Student@1234`
- **Student 2**: `bob@university.edu` / `Student@1234`

### 2. Run Client Web Dashboard (React + Vite + TypeScript)
```bash
cd client
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173). The dashboard includes an **interactive in-browser BLE Beacon Simulator** to test token rotation and student attendance directly from the UI without physical phones.

### 3. Run Server Integration Test Suite
```bash
python -m pytest server/tests -v
```
*(All 7 tests pass: registration, password hashing, HMAC determinism, grace window expiry, binary packing/unpacking, device mismatch blocking, and weak RSSI rejection).*

---

## Turnkey Docker Deployment

To launch the full production stack (FastAPI Backend, PostgreSQL 16, Redis 7, and Nginx React Dashboard):

```bash
cd docker
docker-compose up --build
```
- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **WebSocket Feeds**: `ws://localhost:8000/ws/sessions/{id}`

---

## Load & Concurrency Stress Testing

Simulate high-volume student arrivals (100, 500, or 1000 students) sending concurrent attendance requests:

```bash
# Test 100 students with 50 concurrent connections
python scripts/load_test.py --students 100 --concurrency 50

# Test 500 students with 100 concurrent connections
python scripts/load_test.py --students 500 --concurrency 100

# Test 1000 students with 200 concurrent connections
python scripts/load_test.py --students 1000 --concurrency 200
```
Measures:
- Throughput (requests/second)
- Latency distribution: min, mean, p50, p95, p99, max
- Rejection accuracy (weak RSSI outside classroom vs valid indoor attendees)

---

## Anti-Proxy Security Guarantees

1. **One Student = One Device**: Hardware UUID (`device_uuid`) permanently bound to student account. Attendance cannot be submitted from another student's phone.
2. **5-Second Rotating Tokens**: Cryptographic HMAC-SHA256 signatures expire in 5 seconds, neutralizing screenshot and messaging app relays.
3. **Physical RF Boundary ($-75\text{ dBm}$ Cutoff)**: Wall and door attenuation ensures students outside the lecture hall are rejected.
4. **Duplicate Prevention**: Database unique constraints enforce exactly one attendance record per session per student.
5. **Real-time Anomaly Detection**: Floods, replay attempts, and hardware mismatches are flagged with `CRITICAL` audit logs streamed to the organizer dashboard.

---

## Developer Architecture Guide

Open `ARCHITECTURE.html` in any browser to explore the interactive visual guide, folder breakdown, and comprehensive technical interview Q&A.
