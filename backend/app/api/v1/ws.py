from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["Real-time WebSockets"])


@router.websocket("/objectives/{objective_id}")
async def websocket_endpoint(websocket: WebSocket, objective_id: str):
    await ws_manager.connect(objective_id, websocket)
    try:
        while True:
            # Keep connection open; receive client pings/messages if sent
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(objective_id, websocket)
