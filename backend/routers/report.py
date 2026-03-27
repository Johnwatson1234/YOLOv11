"""Post-class Report & AI Insights API."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.data_service import get_report_data
from services.llm_service import generate_report_local

router = APIRouter(prefix="/api/v1/report", tags=["Report"])


class ReportGenRequest(BaseModel):
    subject: str = "数据结构"
    course_time: str = "14:00-14:45"
    teaching_focus: str = ""
    schedule_id: int = 1


@router.get("/data/{schedule_id}")
async def report_data(schedule_id: int = 1):
    """Get post-class analysis data (focus curve, behavior distribution)."""
    data = get_report_data(schedule_id)
    return {"code": 0, "data": data}


@router.post("/generate")
async def generate_ai_report(req: ReportGenRequest):
    """Generate AI evaluation report."""
    data = get_report_data(req.schedule_id)
    focus_curve = data["focus_curve"]

    # Calculate early/late focus
    early = [p["score"] for p in focus_curve if p["minute"] <= 20]
    late = [p["score"] for p in focus_curve if p["minute"] > 25]
    early_focus = round(sum(early) / len(early), 1) if early else 90
    late_focus = round(sum(late) / len(late), 1) if late else 65

    report_text = generate_report_local(
        subject=req.subject,
        course_time=req.course_time,
        teaching_focus=req.teaching_focus or "未填写教学重难点",
        total_students=data["total_students"],
        early_focus=early_focus,
        late_focus=late_focus,
        distracted_count=max(1, int(data["total_students"] * (1 - late_focus / 100))),
    )

    return {
        "code": 0,
        "data": {
            "report_text": report_text,
            "suggested_tags": ["需加强互动", "节奏优化", "关注后排"],
        }
    }


@router.get("/history")
async def report_history():
    """Get list of past course reports."""
    from datetime import datetime, timedelta
    import random
    history = []
    subjects = ["数据结构", "操作系统", "计算机网络", "计算机组成原理", "数据库原理", "软件工程"]
    for i in range(10):
        d = datetime.now() - timedelta(days=i)
        history.append({
            "schedule_id": i + 1,
            "subject": subjects[i % len(subjects)],
            "date": d.strftime("%Y-%m-%d"),
            "time_range": f"{8 + (i % 4) * 2}:00-{8 + (i % 4) * 2}:45",
            "avg_focus": round(random.uniform(65, 95), 1),
            "class_id": "计科2301班",
        })
    return {"code": 0, "data": history}
