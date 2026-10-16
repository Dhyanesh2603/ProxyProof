import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("proxyproof.websocket")

class ConnectionManager:
    def __init__(self):
        # Maps session_id (int) -> Set[WebSocket]
        self.session_subscribers: Dict[int, Set[WebSocket]] = {}
        # Global subscribers (all admin/organizer live feeds)
        self.global_subscribers: Set[WebSocket] = set()

    async def connect_session(self, session_id: int, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.session_subscribers:
            self.session_subscribers[session_id] = set()
        self.session_subscribers[session_id].add(websocket)
        logger.info(f"WebSocket client connected to session {session_id}. Total: {len(self.session_subscribers[session_id])}")

    def disconnect_session(self, session_id: int, websocket: WebSocket):
        if session_id in self.session_subscribers:
            self.session_subscribers[session_id].discard(websocket)
            if not self.session_subscribers[session_id]:
                del self.session_subscribers[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}.")

    async def connect_global(self, websocket: WebSocket):
        await websocket.accept()
        self.global_subscribers.add(websocket)
        logger.info(f"WebSocket client connected to global channel. Total: {len(self.global_subscribers)}")

    def disconnect_global(self, websocket: WebSocket):
        self.global_subscribers.discard(websocket)
        logger.info("WebSocket client disconnected from global channel.")

    async def broadcast_session(self, session_id: int, message: dict):
        if session_id in self.session_subscribers:
            dead_sockets = set()
            payload = json.dumps(message)
            for ws in self.session_subscribers[session_id]:
                try:
                    await ws.send_text(payload)
                except Exception as e:
                    logger.warning(f"Error sending message to session ws: {e}")
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.session_subscribers[session_id].discard(ws)

        # Also push to global subscribers
        await self.broadcast_global(message)

    async def broadcast_global(self, message: dict):
        dead_sockets = set()
        payload = json.dumps(message)
        for ws in self.global_subscribers:
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending message to global ws: {e}")
                dead_sockets.add(ws)
        for ws in dead_sockets:
            self.global_subscribers.discard(ws)

ws_manager = ConnectionManager()
