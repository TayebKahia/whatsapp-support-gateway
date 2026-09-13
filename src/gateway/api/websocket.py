import datetime
import logging
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from gateway.channel.base import WhatsAppChannelPort
from gateway.repository.session import SessionStore

logger = logging.getLogger(__name__)


class OperatorConnectionManager:
    """Manages real-time WebSocket connections between human support operators and active sessions."""

    def __init__(self) -> None:
        self._active_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, phone: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections[phone].add(websocket)
        logger.info("Operator connected to live session for %s", phone)

    def disconnect(self, phone: str, websocket: WebSocket) -> None:
        if phone in self._active_connections:
            self._active_connections[phone].discard(websocket)
            if not self._active_connections[phone]:
                del self._active_connections[phone]
        logger.info("Operator disconnected from live session for %s", phone)

    async def broadcast_to_phone(self, phone: str, message: dict[str, Any]) -> None:
        """Broadcast an event payload to all operator consoles monitoring this phone number."""
        sockets = list(self._active_connections.get(phone, set()))
        if not sockets:
            return

        dead_sockets: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except (WebSocketDisconnect, RuntimeError, ConnectionResetError, OSError):
                dead_sockets.append(ws)

        for dead_ws in dead_sockets:
            self.disconnect(phone, dead_ws)


def create_websocket_router(
    manager: OperatorConnectionManager,
    channel: WhatsAppChannelPort,
    session_store: SessionStore,
) -> APIRouter:
    router = APIRouter(tags=["Live Operator WebSocket"])

    @router.websocket("/ws/operator/{phone}")
    async def operator_chat_endpoint(websocket: WebSocket, phone: str) -> None:
        await manager.connect(phone, websocket)
        try:
            # Send initial confirmation of live bridge attachment
            await websocket.send_json(
                {
                    "type": "connection_established",
                    "phone": phone,
                    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                }
            )

            while True:
                data = await websocket.receive_json()
                text = data.get("text", "").strip()
                if not text:
                    continue

                logger.info("Operator sending direct message to %s: %s", phone, text)

                # 1. Dispatch outbound WhatsApp message via configured channel
                await channel.send_text(phone, text)

                # 2. Append operator reply to persistent customer transcript
                session_store.append_transcript(phone, role="agent", message=text)

                # 3. Echo the dispatched message back to any open operator tabs
                echo_payload = {
                    "type": "operator_message",
                    "role": "agent",
                    "text": text,
                    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                }
                await manager.broadcast_to_phone(phone, echo_payload)

        except WebSocketDisconnect:
            manager.disconnect(phone, websocket)
        except (RuntimeError, ConnectionResetError, OSError) as exc:
            logger.warning("Operator WebSocket ended for %s: %s", phone, exc)
            manager.disconnect(phone, websocket)

    return router
