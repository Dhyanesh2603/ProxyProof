from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def normalize_compare(dt1: datetime, dt2: datetime) -> tuple[datetime, datetime]:
    """
    Ensures two datetimes can be safely compared across SQLite/Postgres.
    If one is naive and the other is aware, normalizes both to naive UTC.
    """
    c1 = dt1
    c2 = dt2
    if c1.tzinfo is not None:
        c1 = c1.astimezone(timezone.utc).replace(tzinfo=None)
    if c2.tzinfo is not None:
        c2 = c2.astimezone(timezone.utc).replace(tzinfo=None)
    return c1, c2
