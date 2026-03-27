"""System Settings & Model Config API."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.data_service import get_settings, update_settings, get_system_metrics
from services.yolo_service import yolo_service

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


class SettingsUpdate(BaseModel):
    current_model: Optional[str] = None
    confidence: Optional[float] = None
    iou: Optional[float] = None
    video_source: Optional[str] = None
    privacy_mode: Optional[bool] = None
    data_retention_days: Optional[int] = None
    auto_cleanup: Optional[bool] = None
    llm_api_url: Optional[str] = None
    llm_api_key: Optional[str] = None


@router.get("/")
async def get_current_settings():
    """Get all system settings."""
    settings = get_settings()
    return {"code": 0, "data": settings}


@router.put("/")
async def update_system_settings(req: SettingsUpdate):
    """Update system settings."""
    updates = req.model_dump(exclude_none=True)

    # Apply model changes to YOLO service
    if "current_model" in updates:
        yolo_service.load_model(updates["current_model"])
    if "confidence" in updates or "iou" in updates:
        yolo_service.update_params(
            confidence=updates.get("confidence"),
            iou=updates.get("iou"),
        )

    new_settings = update_settings(updates)
    return {"code": 0, "data": new_settings, "message": "Settings updated"}


@router.get("/metrics")
async def system_metrics():
    """Get real-time hardware metrics."""
    return {"code": 0, "data": get_system_metrics()}


@router.get("/models")
async def available_models():
    """List available model files."""
    import config
    models = []
    for name, path in config.MODEL_FILES.items():
        from pathlib import Path
        exists = Path(path).exists()
        models.append({"name": name, "path": path, "available": exists})
    return {"code": 0, "data": models}


@router.post("/test_llm")
async def test_llm_connection(api_url: str = "", api_key: str = ""):
    """Test LLM API connectivity."""
    if not api_url or not api_key:
        return {"code": 1, "message": "请填写 API 地址和密钥"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(api_url.rstrip("/") + "/models",
                                    headers={"Authorization": f"Bearer {api_key}"})
            if resp.status_code == 200:
                return {"code": 0, "message": "连接成功 ✅"}
            else:
                return {"code": 1, "message": f"连接失败: HTTP {resp.status_code}"}
    except Exception as e:
        return {"code": 1, "message": f"连接失败: {str(e)}"}
