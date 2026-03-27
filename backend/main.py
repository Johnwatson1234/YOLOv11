"""ClassVision (慧眼课堂) — FastAPI Backend Entry Point."""
import sys
from pathlib import Path

# Ensure backend directory is in the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import dashboard, monitor, attendance, report, student, alert, settings

app = FastAPI(
    title="慧眼课堂 ClassVision API",
    description="智能教学评估系统后端 — 基于 YOLOv11 的课堂行为检测与分析",
    version="2.1.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(monitor.router)
app.include_router(attendance.router)
app.include_router(report.router)
app.include_router(student.router)
app.include_router(alert.router)
app.include_router(settings.router)


@app.get("/")
async def root():
    return {
        "name": "慧眼课堂 ClassVision",
        "version": "2.1.0",
        "status": "running",
        "api_docs": "/docs",
    }


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    from services.yolo_service import yolo_service
    from services.video_service import video_service
    
    print("=" * 60)
    print("  慧眼课堂 ClassVision — 智能教学评估系统")
    print("  Powered by YOLOv11 + FastAPI + Vue 3")
    print("=" * 60)
    
    # Pre-load model
    yolo_service.load_model()
    # Pre-open video
    video_service.open()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
