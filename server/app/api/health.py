import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.redis_cache import cache

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    cache_status = "in-memory-fallback"
    try:
        if cache._is_redis:
            cache_status = "redis-connected"
    except Exception:
        pass

    return {
        "status": "online",
        "service": "ProxyProof Backend",
        "version": "1.0.0",
        "timestamp": time.time(),
        "database": db_status,
        "cache": cache_status
    }
