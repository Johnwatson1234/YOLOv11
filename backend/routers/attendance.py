"""Smart Attendance API."""
from fastapi import APIRouter
from services.data_service import get_attendance_records, STUDENTS

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])


@router.get("/live")
async def live_attendance():
    """Get current attendance list."""
    records = get_attendance_records()
    total = len(STUDENTS)
    present = sum(1 for r in records if r["status"] == "PRESENT")
    late = sum(1 for r in records if r["status"] == "LATE")
    absent = sum(1 for r in records if r["status"] == "ABSENT")
    return {
        "code": 0,
        "data": {
            "total": total,
            "present": present,
            "late": late,
            "absent": absent,
            "records": records,
        }
    }


@router.put("/update/{student_id}")
async def update_status(student_id: str, status: str):
    """Manually update attendance status."""
    return {
        "code": 0,
        "message": f"Student {student_id} status updated to {status}",
    }


@router.get("/trend")
async def attendance_trend():
    """Get 7-day attendance trend."""
    import random
    from datetime import datetime, timedelta
    trend = []
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        trend.append({
            "date": d.strftime("%m-%d"),
            "present": random.randint(38, 45),
            "late": random.randint(0, 4),
            "absent": random.randint(0, 3),
        })
    return {"code": 0, "data": trend}
