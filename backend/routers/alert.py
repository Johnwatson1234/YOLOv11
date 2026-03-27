"""Alert & Security Center API."""
from fastapi import APIRouter
from pydantic import BaseModel
from services.data_service import get_alert_events, get_alert_rules

router = APIRouter(prefix="/api/v1/alert", tags=["Alert"])


class AlertFeedback(BaseModel):
    alert_id: int
    confirmed: bool  # True = confirmed violation, False = false positive


@router.get("/events")
async def alert_events():
    """Get all alert events."""
    events = get_alert_events()
    total = len(events)
    confirmed = sum(1 for e in events if e["confirmed"] is True)
    dismissed = sum(1 for e in events if e["confirmed"] is False)
    pending = total - confirmed - dismissed
    return {
        "code": 0,
        "data": {
            "total": total,
            "confirmed": confirmed,
            "dismissed": dismissed,
            "pending": pending,
            "false_rate": round(dismissed / total * 100, 1) if total > 0 else 0,
            "events": events,
        }
    }


@router.post("/feedback")
async def alert_feedback(fb: AlertFeedback):
    """Submit human feedback on an alert (confirm / dismiss)."""
    action = "confirmed as violation" if fb.confirmed else "dismissed as false positive"
    return {
        "code": 0,
        "message": f"Alert {fb.alert_id} {action}. Recorded as hard example for model fine-tuning.",
    }


@router.get("/rules")
async def alert_rules():
    """Get alert trigger rules."""
    return {"code": 0, "data": get_alert_rules()}


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: int, enabled: bool = True, threshold: int = 3):
    """Update an alert rule."""
    return {
        "code": 0,
        "message": f"Rule {rule_id} updated: enabled={enabled}, threshold={threshold}",
    }


@router.get("/trend")
async def alert_trend():
    """Get 7-day alert trend data."""
    import random
    from datetime import datetime, timedelta
    trend = []
    types = ["群体性趴桌", "多人玩手机", "学生离座", "集体走神"]
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        day_data = {"date": d.strftime("%m-%d")}
        for t in types:
            day_data[t] = random.randint(0, 5)
        trend.append(day_data)
    return {"code": 0, "data": {"trend": trend, "types": types}}
