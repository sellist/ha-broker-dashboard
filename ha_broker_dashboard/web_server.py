import asyncio
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .data_store import DataStore
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def create_app(data_store: DataStore, ws_manager: WebSocketManager) -> FastAPI:
    app = FastAPI(title="HA Broker Dashboard")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        html_path = STATIC_DIR / "index.html"
        if html_path.exists():
            return html_path.read_text(encoding="utf-8")
        return "<html><body><h1>Dashboard</h1><p>Static files not found.</p></body></html>"

    @app.get("/api/sensors")
    async def get_sensors():
        return data_store.get_all_sensors()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)

        await ws_manager.send_personal(
            websocket, {"type": "init", "data": data_store.get_all_sensors()}
        )

        try:
            while True:
                data = await websocket.receive_text()
                logger.debug(f"Received from client: {data}")
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


async def broadcast_sensor_update(
    ws_manager: WebSocketManager, topic: str, sensor_data: dict[str, Any]
) -> None:
    await ws_manager.broadcast(
        {"type": "update", "topic": topic, "data": sensor_data}
    )

