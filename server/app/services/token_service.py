import time
import json
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.session import AttendanceSession
from app.models.rotating_token import RotatingToken
from app.security.crypto_tokens import (
    compute_rotating_token,
    get_current_window_index,
    generate_current_token,
    verify_rotating_token,
    pack_ble_payload
)
from app.services.redis_cache import cache
from app.config import settings

class TokenService:
    @staticmethod
    def get_or_create_active_token(db: Session, session: AttendanceSession) -> Dict[str, Any]:
        """
        Retrieves or generates the currently valid rotating token for an active session.
        Caches in Redis for sub-millisecond retrieval by BLE broadcasting agents or APIs.
        """
        now = time.time()
        interval = session.token_rotation_interval or settings.ROTATING_TOKEN_INTERVAL_SECONDS
        window_idx = get_current_window_index(now, interval)
        
        cache_key = f"session_token:{session.id}:{window_idx}"
        cached = cache.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass

        token = compute_rotating_token(session.id, session.secret_key, window_idx)
        valid_from = float(window_idx * interval)
        valid_until = float((window_idx + 1) * interval)
        
        payload_bytes = pack_ble_payload(session.id, token, window_idx)
        payload_hex = payload_bytes.hex()
        
        data = {
            "session_id": session.id,
            "session_code": session.session_code,
            "token": token,
            "window_index": window_idx,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "time_remaining_seconds": max(0.0, valid_until - now),
            "ble_payload_hex": payload_hex,
            "rotation_interval_seconds": interval
        }
        
        # Cache for TTL = interval * 3
        cache.set(cache_key, json.dumps(data), ex=interval * 3)
        return data

    @staticmethod
    def validate_token(
        db: Session,
        session: AttendanceSession,
        token_candidate: str
    ) -> Tuple[bool, str]:
        """
        Cryptographically validates if token_candidate matches the current or acceptable grace window.
        """
        interval = session.token_rotation_interval or settings.ROTATING_TOKEN_INTERVAL_SECONDS
        grace = settings.ROTATING_TOKEN_GRACE_WINDOWS
        return verify_rotating_token(
            session_id=session.id,
            secret_key=session.secret_key,
            token_candidate=token_candidate,
            interval=interval,
            grace_windows=grace
        )
