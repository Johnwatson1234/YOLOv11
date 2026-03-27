"""Dashboard API — system overview and quick stats."""
from fastapi import APIRouter
from services.data_service import (
    get_dashboard_stats, get_course_schedule, get_weekly_trend, get_notifications
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def dashboard_stats():
    return {"code": 0, "data": get_dashboard_stats()}


@router.get("/schedule")
async def today_schedule():
    return {"code": 0, "data": get_course_schedule()}


@router.get("/trend")
async def weekly_trend():
    return {"code": 0, "data": get_weekly_trend()}


@router.get("/notifications")
async def notifications():
    return {"code": 0, "data": get_notifications()}
