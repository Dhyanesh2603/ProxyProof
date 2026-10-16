from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.sessions import router as sessions_router
from app.api.attendance import router as attendance_router
from app.api.devices import router as devices_router
from app.api.analytics import router as analytics_router
from app.api.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(sessions_router)
api_router.include_router(attendance_router)
api_router.include_router(devices_router)
api_router.include_router(analytics_router)
