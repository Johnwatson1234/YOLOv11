"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    LATE = "LATE"
    ABSENT = "ABSENT"


class BehaviorType(str, Enum):
    Listening = "Listening"
    Reading_Writing = "Reading_Writing"
    Sleeping = "Sleeping"
    Looking_Around = "Looking_Around"
    Using_Phone = "Using_Phone"
    Standing_Leaving = "Standing_Leaving"


class DetectedObject(BaseModel):
    track_id: str
    student_id: Optional[str] = None
    bbox: list[float]  # [x_center, y_center, width, height] relative 0~1
    action: str
    confidence: float


class FrameMetrics(BaseModel):
    total: int
    focus: int
    distracted: int
    violation: int = 0
    score: float


class FrameData(BaseModel):
    timestamp: int
    frame_id: int
    metrics: FrameMetrics
    objects: list[DetectedObject]


class StudentInfo(BaseModel):
    student_id: str
    name: str
    class_id: str
    avatar: Optional[str] = None


class AttendanceRecord(BaseModel):
    student_id: str
    name: str
    class_id: str
    status: AttendanceStatus
    check_in_time: Optional[str] = None


class CourseSchedule(BaseModel):
    schedule_id: int
    class_id: str
    teacher_id: str
    subject: str
    start_time: str
    end_time: str
    is_active: bool = False


class AlertEvent(BaseModel):
    alert_id: int
    alert_type: str
    severity: str  # "warning", "danger"
    description: str
    timestamp: str
    student_ids: list[str] = []
    snapshot_url: Optional[str] = None
    confirmed: Optional[bool] = None


class AlertRule(BaseModel):
    rule_id: int
    name: str
    condition: str
    threshold: int
    enabled: bool = True


class SystemSettings(BaseModel):
    current_model: str = "yolov11.pt"
    confidence: float = 0.45
    iou: float = 0.5
    video_source: str = ""
    privacy_mode: bool = False
    data_retention_days: int = 30
    auto_cleanup: bool = True
    llm_api_url: str = ""
    llm_api_key: str = ""


class ReportRequest(BaseModel):
    class_id: str = "ClassA"
    course_time: str = "14:00-14:45"
    subject: str = "数据结构"
    teaching_focus: str = ""
    focus_data: list[dict] = []


class StudentProfile(BaseModel):
    student_id: str
    name: str
    class_id: str
    avatar: Optional[str] = None
    attendance_rate: float = 0.0
    avg_focus_score: float = 0.0
    radar_data: dict = {}
    trend_data: list[dict] = []
    behavior_stats: dict = {}
    recent_records: list[dict] = []


class DashboardStats(BaseModel):
    weekly_hours: float = 0.0
    avg_attendance_rate: float = 0.0
    avg_focus_score: float = 0.0
    pending_alerts: int = 0


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None
