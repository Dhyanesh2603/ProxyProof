import json
import time
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.services.redis_cache import cache

logger = logging.getLogger("proxyproof.anomaly")

class AnomalyService:
    @staticmethod
    def check_rate_limit(student_id: int, window_seconds: int = 5, max_attempts: int = 5) -> bool:
        """
        Returns True if rate limit is exceeded (anomaly detected).
        """
        key = f"rate_limit:{student_id}"
        attempts = cache.incr(key)
        if attempts == 1:
            cache.set(key, "1", ex=window_seconds)
        return attempts > max_attempts

    @staticmethod
    def log_suspicious_activity(
        db: Session,
        event_type: str,
        user_id: Optional[int],
        details: dict,
        severity: str = "WARNING",
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Records a security anomaly or audit trail event.
        """
        log_entry = AuditLog(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            details=json.dumps(details),
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        logger.warning(f"SECURITY ALERT [{severity}] {event_type}: user_id={user_id} details={details}")
        return log_entry
