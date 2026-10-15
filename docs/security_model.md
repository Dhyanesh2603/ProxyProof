# ProxyProof Security Architecture & Anti-Proxy Threat Model

## 1. Threat Model & Attack Vector Analysis

| Attack Vector | Attacker Action | ProxyProof Defense Mechanism |
| :--- | :--- | :--- |
| **Credential Sharing Proxy** | Absent student gives password to a classmate present in room | **Hardware Device Binding**: The classmate's phone UUID does not match the absent student's registered UUID. Attempt rejected with `DEVICE_HARDWARE_MISMATCH`. |
| **Screenshot / WhatsApp Relay** | Present student copies token and texts it to absent student | **Short Rotation Window ($5\text{s}$)**: By the time the token is screenshotted, forwarded, and submitted over WAN, the token window has expired (`INVALID_OR_EXPIRED_ROTATING_TOKEN`). |
| **Hallway / Outdoor Sniffing** | Student stands outside classroom door or in hallway | **Strict RSSI Cutoff ($-75\text{ dBm}$)**: Concrete walls attenuate BLE signal to $\le -82\text{ dBm}$. Backend rejects with `PROXIMITY_RSSI_TOO_WEAK`. |
| **Packet Replay Attack** | Attacker replays previously captured BLE advertisement | **Window-Index Nonce Tracking**: Tokens are valid only within their discrete 5-second interval. Additionally, successful attendance for that session blocks duplicate submissions. |
| **Emulator / Multi-Account Automation** | Running automated scripts / Android emulator to mark 50 friends | **Multi-Student Device Collision Alert**: Two active users cannot bind to the same hardware UUID. Rapid submissions from single IP/device flag `SUSPICIOUS_RAPID_ATTENDANCE` audit log. |
| **Device Swap Abuse** | Student claims they "lost their phone" to bind friend's phone | **Organizer Approval Workflow**: Device binding cannot be changed arbitrarily. Student submits request with justification; Organizer reviews and approves on the dashboard. |

---

## 2. The 8-Step Verification Pipeline

Every incoming `POST /api/v1/attendance/mark` payload passes through an atomic 8-step verification pipeline in `AttendanceService`:

```
                       [Incoming Attendance Payload]
                         (session_id, token, device_uuid, rssi)
                                     |
                                     v
                        +--------------------------+
                        | 1. Student Status Check  |-----> Inactive / Missing? -> 401 Unauthorized
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 2. Device Hardware Match |-----> Mismatch? -> REJECTED (Spoof Alert)
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 3. Active Session Status |-----> Inactive / Ended? -> REJECTED
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 4. Session Time Window   |-----> Session Expired? -> REJECTED
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 5. Duplicate Check       |-----> Already Marked? -> REJECTED (Duplicate)
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 6. RSSI Proximity Check  |-----> RSSI < Threshold? -> REJECTED (Weak Signal)
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 7. HMAC Token Crypto     |-----> Signature Expired? -> REJECTED (Invalid Token)
                        +--------------------------+
                                     | (Pass)
                                     v
                        +--------------------------+
                        | 8. Status Classification |
                        |    (PRESENT vs LATE)     |
                        +--------------------------+
                                     |
                                     v
                        [DB Write & Real-Time WS Broadcast]
```

---

## 3. Heuristic Anomaly Engine & Audit Logs

Any failed verification attempt produces an `AuditLog` entry classified into:
- `INFO`: Normal system events (session created, attendance marked, device registered).
- `WARNING`: Out-of-bounds signal strength (`OUT_OF_BOUNDS_RSSI_DETECTED`), expired rotating token submission.
- `CRITICAL`: Hardware device spoofing attempts (`UNAUTHORIZED_DEVICE_SPOOF_ATTEMPT`), rapid attendance burst anomalies (`SUSPICIOUS_RAPID_ATTENDANCE`), multiple student collision on single hardware ID.

All logs are streamed to the organizer console in real time via WebSockets.
