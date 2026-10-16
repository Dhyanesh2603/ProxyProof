from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api import api_router
from app.middleware.logging import LoggingMiddleware
from app.websocket.manager import ws_manager
from app.utils.seed_data import seed_database
import app.models  # Ensure all models are registered in Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed demo data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise BLE-Based Smart Attendance Platform with Rotating Tokens & Anti-Proxy Verification",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# WebSockets
@app.websocket("/ws/sessions/{session_id}")
async def websocket_session_endpoint(websocket: WebSocket, session_id: int):
    await ws_manager.connect_session(session_id, websocket)
    try:
        while True:
            # Keep socket alive and accept ping/pong or client queries
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_session(session_id, websocket)
    except Exception:
        ws_manager.disconnect_session(session_id, websocket)

@app.websocket("/ws/events")
async def websocket_global_endpoint(websocket: WebSocket):
    await ws_manager.connect_global(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_global(websocket)
    except Exception:
        ws_manager.disconnect_global(websocket)

@app.get("/")
def root():
    return {
        "service": "ProxyProof API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
