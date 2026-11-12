import json
from typing import Dict, List
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # Maps objective_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, objective_id: str, websocket: WebSocket):
        await websocket.accept()
        if objective_id not in self.active_connections:
            self.active_connections[objective_id] = []
        self.active_connections[objective_id].append(websocket)

    def disconnect(self, objective_id: str, websocket: WebSocket):
        if objective_id in self.active_connections:
            if websocket in self.active_connections[objective_id]:
                self.active_connections[objective_id].remove(websocket)
            if not self.active_connections[objective_id]:
                del self.active_connections[objective_id]

    async def broadcast(self, objective_id: str, message: dict):
        if objective_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[objective_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(objective_id, dead)


ws_manager = WebSocketManager()
