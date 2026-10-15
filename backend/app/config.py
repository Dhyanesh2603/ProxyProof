import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProxyProof"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "proxyproof-super-secure-production-master-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./proxyproof.db")
    
    # Redis / In-Memory Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # BLE Attendance Security Parameters
    ROTATING_TOKEN_INTERVAL_SECONDS: int = 5  # Rotating interval (e.g. 5 seconds)
    ROTATING_TOKEN_GRACE_WINDOWS: int = 1     # Accept current window + 1 previous window
    DEFAULT_RSSI_THRESHOLD: int = -75          # dBm: reject signals weaker than -75 dBm (outside classroom)
    ATTENDANCE_LATE_THRESHOLD_MINUTES: int = 15 # After 15 minutes of session start, mark as LATE
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
