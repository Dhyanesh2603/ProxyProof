import hmac
import hashlib
import time
import secrets
import struct
from typing import Tuple, Optional, List
from app.config import settings

def generate_session_secret() -> str:
    """Generate a high-entropy 256-bit cryptographic key for a session."""
    return secrets.token_hex(32)

def get_current_window_index(timestamp: Optional[float] = None, interval: Optional[int] = None) -> int:
    """Calculate the discrete time window index."""
    ts = timestamp if timestamp is not None else time.time()
    step = interval if interval is not None else settings.ROTATING_TOKEN_INTERVAL_SECONDS
    return int(ts // step)

def compute_rotating_token(
    session_id: int,
    secret_key: str,
    window_index: int
) -> str:
    """
    Generate a deterministic HMAC-SHA256 rotating token for a specific session and time window.
    Truncated to 16 hex chars (64-bit entropy) for high security and compact BLE payload.
    """
    msg = f"PROXYPROOF:{session_id}:{window_index}".encode("utf-8")
    key = secret_key.encode("utf-8")
    digest = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return digest[:16]

def generate_current_token(
    session_id: int,
    secret_key: str,
    interval: Optional[int] = None
) -> Tuple[str, int, float, float]:
    """
    Returns (token, window_index, valid_from, valid_until) for the current moment.
    """
    step = interval if interval is not None else settings.ROTATING_TOKEN_INTERVAL_SECONDS
    now = time.time()
    w_idx = get_current_window_index(now, step)
    token = compute_rotating_token(session_id, secret_key, w_idx)
    valid_from = float(w_idx * step)
    valid_until = float((w_idx + 1) * step)
    return token, w_idx, valid_from, valid_until

def verify_rotating_token(
    session_id: int,
    secret_key: str,
    token_candidate: str,
    server_time: Optional[float] = None,
    interval: Optional[int] = None,
    grace_windows: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Verifies if token_candidate matches the current or acceptable grace window tokens.
    Returns (is_valid, matched_window_info).
    """
    now = server_time if server_time is not None else time.time()
    step = interval if interval is not None else settings.ROTATING_TOKEN_INTERVAL_SECONDS
    grace = grace_windows if grace_windows is not None else settings.ROTATING_TOKEN_GRACE_WINDOWS
    
    current_w = get_current_window_index(now, step)
    
    # We check: [current_w, current_w - 1, ... current_w - grace, current_w + 1 (slight client clock advance)]
    candidate_windows = [current_w]
    for g in range(1, grace + 1):
        candidate_windows.append(current_w - g)
    candidate_windows.append(current_w + 1)
    
    clean_candidate = token_candidate.strip().lower()
    
    for w in candidate_windows:
        expected = compute_rotating_token(session_id, secret_key, w).lower()
        if hmac.compare_digest(clean_candidate, expected):
            return True, f"Matched window {w} (offset {w - current_w})"
            
    return False, "Token expired or invalid HMAC signature"

def pack_ble_payload(session_id: int, token: str, window_index: int) -> bytes:
    """
    Pack data into a compact binary BLE manufacturer payload (26 bytes).
    Format:
    - 2 bytes: Magic Prefix 0x5050 ('PP')
    - 4 bytes: Session ID (uint32)
    - 4 bytes: Window Index (uint32)
    - 16 bytes: ASCII token string (16 characters)
    Total: 26 bytes (fits inside standard 31-byte BLE advertising frame).
    """
    token_bytes = token.encode("ascii")[:16].ljust(16, b"\x00")
    header = struct.pack(">HII", 0x5050, session_id, window_index)
    return header + token_bytes

def unpack_ble_payload(payload: bytes) -> Optional[dict]:
    """
    Unpack binary BLE manufacturer payload.
    """
    if len(payload) < 26:
        return None
    magic, session_id, window_index = struct.unpack(">HII", payload[:10])
    if magic != 0x5050:
        return None
    token = payload[10:26].decode("ascii", errors="ignore").rstrip("\x00")
    return {
        "session_id": session_id,
        "window_index": window_index,
        "token": token
    }
