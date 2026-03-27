"""Real-time monitoring API — video stream + WebSocket for YOLO detections."""
import asyncio
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from services.yolo_service import yolo_service
from services.video_service import video_service
import config

router = APIRouter(prefix="/api/v1/monitor", tags=["Monitor"])

# Active WebSocket connections
_ws_clients: list[WebSocket] = []
_inference_task: asyncio.Task | None = None
_is_monitoring: bool = False


@router.get("/video_feed")
async def video_feed():
    """MJPEG video stream endpoint for the <img> or <video> tag."""
    if not video_service.cap or not video_service.cap.isOpened():
        video_service.open()

    return StreamingResponse(
        video_service.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/video_info")
async def video_info():
    """Get video source metadata."""
    if not video_service.cap:
        video_service.open()
    return {"code": 0, "data": video_service.get_info()}


@router.post("/start")
async def start_monitoring():
    """Start the YOLO inference loop."""
    global _is_monitoring, _inference_task

    if _is_monitoring:
        return {"code": 0, "message": "Already monitoring"}

    # Load model if not loaded
    if yolo_service.model is None:
        yolo_service.load_model()

    # Open video if not open
    if not video_service.cap or not video_service.cap.isOpened():
        video_service.open()

    _is_monitoring = True
    _inference_task = asyncio.create_task(_inference_loop())
    return {"code": 0, "message": "Monitoring started"}


@router.post("/stop")
async def stop_monitoring():
    """Stop the YOLO inference loop."""
    global _is_monitoring, _inference_task

    _is_monitoring = False
    if _inference_task:
        _inference_task.cancel()
        _inference_task = None
    return {"code": 0, "message": "Monitoring stopped"}


@router.get("/status")
async def monitoring_status():
    """Get current monitoring status."""
    return {
        "code": 0,
        "data": {
            "is_monitoring": _is_monitoring,
            "model": yolo_service.model_name,
            "confidence": yolo_service.confidence,
            "iou": yolo_service.iou,
            "clients": len(_ws_clients),
        }
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection data push."""
    await websocket.accept()
    _ws_clients.append(websocket)
    print(f"[WS] Client connected. Total: {len(_ws_clients)}")

    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Client can send control commands
            try:
                msg = json.loads(data)
                if msg.get("action") == "start" and not _is_monitoring:
                    await start_monitoring()
                elif msg.get("action") == "stop":
                    await stop_monitoring()
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        _ws_clients.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(_ws_clients)}")


async def _inference_loop():
    """Background loop: read frames → YOLO inference → broadcast via WebSocket."""
    global _is_monitoring

    while _is_monitoring:
        if not _ws_clients:
            await asyncio.sleep(0.5)
            continue

        frame = video_service.read_frame()
        if frame is None:
            await asyncio.sleep(0.1)
            continue

        # Run inference
        result = yolo_service.infer_frame(frame)

        # Broadcast to all connected clients
        message = json.dumps(result, ensure_ascii=False)
        disconnected = []
        for ws in _ws_clients:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            _ws_clients.remove(ws)

        await asyncio.sleep(config.WS_PUSH_INTERVAL)
