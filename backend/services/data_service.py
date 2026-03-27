"""Mock data service for ClassVision — provides simulated data for all 7 pages."""
import random
import time
from datetime import datetime, timedelta

# ─── Student Registry ───
STUDENTS = [
    {"student_id": "202301", "name": "张三", "class_id": "计科2301班"},
    {"student_id": "202302", "name": "李四", "class_id": "计科2301班"},
    {"student_id": "202303", "name": "王五", "class_id": "计科2301班"},
    {"student_id": "202304", "name": "赵六", "class_id": "计科2301班"},
    {"student_id": "202305", "name": "孙七", "class_id": "计科2301班"},
    {"student_id": "202306", "name": "周八", "class_id": "计科2301班"},
    {"student_id": "202307", "name": "吴九", "class_id": "计科2301班"},
    {"student_id": "202308", "name": "郑十", "class_id": "计科2301班"},
    {"student_id": "202309", "name": "刘一", "class_id": "计科2301班"},
    {"student_id": "202310", "name": "陈二", "class_id": "计科2301班"},
    {"student_id": "202311", "name": "林小明", "class_id": "计科2301班"},
    {"student_id": "202312", "name": "黄小丽", "class_id": "计科2301班"},
    {"student_id": "202313", "name": "杨晓红", "class_id": "计科2301班"},
    {"student_id": "202314", "name": "何大伟", "class_id": "计科2301班"},
    {"student_id": "202315", "name": "马云飞", "class_id": "计科2301班"},
    {"student_id": "202316", "name": "徐志远", "class_id": "计科2301班"},
    {"student_id": "202317", "name": "朱丽华", "class_id": "计科2301班"},
    {"student_id": "202318", "name": "胡建国", "class_id": "计科2301班"},
    {"student_id": "202319", "name": "高雅琴", "class_id": "计科2301班"},
    {"student_id": "202320", "name": "罗志强", "class_id": "计科2301班"},
    {"student_id": "202321", "name": "梁思思", "class_id": "计科2301班"},
    {"student_id": "202322", "name": "宋文杰", "class_id": "计科2301班"},
    {"student_id": "202323", "name": "唐一诺", "class_id": "计科2301班"},
    {"student_id": "202324", "name": "韩雪", "class_id": "计科2301班"},
    {"student_id": "202325", "name": "冯晓宇", "class_id": "计科2301班"},
    {"student_id": "202326", "name": "董子健", "class_id": "计科2301班"},
    {"student_id": "202327", "name": "程雨涵", "class_id": "计科2301班"},
    {"student_id": "202328", "name": "曾宇航", "class_id": "计科2301班"},
    {"student_id": "202329", "name": "彭美琪", "class_id": "计科2301班"},
    {"student_id": "202330", "name": "萧风", "class_id": "计科2301班"},
    {"student_id": "202331", "name": "蔡依林", "class_id": "计科2301班"},
    {"student_id": "202332", "name": "潘长江", "class_id": "计科2301班"},
    {"student_id": "202333", "name": "田甜", "class_id": "计科2301班"},
    {"student_id": "202334", "name": "贾宝玉", "class_id": "计科2301班"},
    {"student_id": "202335", "name": "丁一", "class_id": "计科2301班"},
    {"student_id": "202336", "name": "余秋雨", "class_id": "计科2301班"},
    {"student_id": "202337", "name": "邓紫棋", "class_id": "计科2301班"},
    {"student_id": "202338", "name": "任达华", "class_id": "计科2301班"},
    {"student_id": "202339", "name": "姚明远", "class_id": "计科2301班"},
    {"student_id": "202340", "name": "卢伟", "class_id": "计科2301班"},
    {"student_id": "202341", "name": "汪涵", "class_id": "计科2301班"},
    {"student_id": "202342", "name": "钟楚红", "class_id": "计科2301班"},
    {"student_id": "202343", "name": "谢天华", "class_id": "计科2301班"},
    {"student_id": "202344", "name": "邹雨", "class_id": "计科2301班"},
    {"student_id": "202345", "name": "段奕宏", "class_id": "计科2301班"},
]

# ─── Course Schedule (today) ───
def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_course_schedule():
    today = get_today_str()
    now = datetime.now()
    courses = [
        {"schedule_id": 1, "class_id": "计科2301班", "teacher_id": "T001", "subject": "数据结构",
         "start_time": f"{today} 08:00", "end_time": f"{today} 08:45"},
        {"schedule_id": 2, "class_id": "计科2301班", "teacher_id": "T002", "subject": "操作系统",
         "start_time": f"{today} 08:55", "end_time": f"{today} 09:40"},
        {"schedule_id": 3, "class_id": "计科2301班", "teacher_id": "T003", "subject": "计算机网络",
         "start_time": f"{today} 10:00", "end_time": f"{today} 10:45"},
        {"schedule_id": 4, "class_id": "计科2301班", "teacher_id": "T001", "subject": "计算机组成原理",
         "start_time": f"{today} 10:55", "end_time": f"{today} 11:40"},
        {"schedule_id": 5, "class_id": "计科2301班", "teacher_id": "T004", "subject": "数据库原理",
         "start_time": f"{today} 14:00", "end_time": f"{today} 14:45"},
        {"schedule_id": 6, "class_id": "计科2301班", "teacher_id": "T005", "subject": "软件工程",
         "start_time": f"{today} 14:55", "end_time": f"{today} 15:40"},
        {"schedule_id": 7, "class_id": "计科2301班", "teacher_id": "T001", "subject": "数据结构",
         "start_time": f"{today} 16:00", "end_time": f"{today} 16:45"},
    ]
    # Mark active course
    for c in courses:
        st = datetime.strptime(c["start_time"], "%Y-%m-%d %H:%M")
        et = datetime.strptime(c["end_time"], "%Y-%m-%d %H:%M")
        c["is_active"] = st <= now <= et
    return courses

# ─── Attendance ───
def get_attendance_records():
    records = []
    statuses = ["PRESENT"] * 38 + ["LATE"] * 4 + ["ABSENT"] * 3
    random.shuffle(statuses)
    for i, s in enumerate(STUDENTS):
        status = statuses[i] if i < len(statuses) else "PRESENT"
        check_in = None
        if status == "PRESENT":
            check_in = f"{get_today_str()} 07:{random.randint(45,59):02d}"
        elif status == "LATE":
            check_in = f"{get_today_str()} 08:{random.randint(6,18):02d}"
        records.append({
            "student_id": s["student_id"],
            "name": s["name"],
            "class_id": s["class_id"],
            "status": status,
            "check_in_time": check_in,
        })
    return records

# ─── Dashboard Stats ───
def get_dashboard_stats():
    return {
        "weekly_hours": round(random.uniform(18, 24), 1),
        "avg_attendance_rate": round(random.uniform(92, 98), 1),
        "avg_focus_score": round(random.uniform(75, 92), 1),
        "pending_alerts": random.randint(2, 8),
    }

# ─── Weekly trend data ───
def get_weekly_trend():
    days = []
    for i in range(6, -1, -1):
        d = datetime.now() - timedelta(days=i)
        days.append({
            "date": d.strftime("%m-%d"),
            "focus_score": round(random.uniform(72, 95), 1),
            "attendance_rate": round(random.uniform(90, 100), 1),
        })
    return days

# ─── Notifications ───
def get_notifications():
    return [
        {"id": 1, "type": "system", "title": "系统版本更新", "content": "慧眼课堂 v2.1.0 已发布，新增隐私脱敏功能", "time": "2026-03-26 08:00"},
        {"id": 2, "type": "model", "title": "模型训练完成", "content": "YOLOv11 教室行为检测模型已更新至最新权重", "time": "2026-03-25 22:30"},
        {"id": 3, "type": "alert", "title": "预警提示", "content": "昨日下午第一节课检测到群体性走神，建议关注", "time": "2026-03-25 17:00"},
        {"id": 4, "type": "system", "title": "数据自动清理", "content": "30天前的违规抓拍截图已自动清理完成", "time": "2026-03-25 03:00"},
        {"id": 5, "type": "model", "title": "模型对比报告", "content": "YOLOv12检测准确率较YOLOv11提升2.3%", "time": "2026-03-24 20:15"},
    ]

# ─── Alert Events ───
_alert_types = ["群体性趴桌", "多人玩手机", "学生长时间离座", "集体走神", "异常聚集"]
_alert_counter = 0

def get_alert_events():
    events = []
    for i in range(15):
        t = datetime.now() - timedelta(hours=random.randint(1, 72))
        atype = random.choice(_alert_types)
        severity = "danger" if "手机" in atype else "warning"
        involved = random.sample([s["student_id"] for s in STUDENTS], random.randint(1, 5))
        events.append({
            "alert_id": i + 1,
            "alert_type": atype,
            "severity": severity,
            "description": f"在课堂视频流中检测到{atype}行为，涉及{len(involved)}名学生",
            "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
            "student_ids": involved,
            "snapshot_url": None,
            "confirmed": None if random.random() > 0.4 else random.choice([True, False]),
        })
    return sorted(events, key=lambda x: x["timestamp"], reverse=True)

# ─── Alert Rules ───
def get_alert_rules():
    return [
        {"rule_id": 1, "name": "群体玩手机预警", "condition": "同时玩手机人数", "threshold": 3, "enabled": True},
        {"rule_id": 2, "name": "群体趴桌预警", "condition": "同时趴桌人数", "threshold": 5, "enabled": True},
        {"rule_id": 3, "name": "学生离座预警", "condition": "离座持续时间(秒)", "threshold": 300, "enabled": True},
        {"rule_id": 4, "name": "专注度低预警", "condition": "全班专注度低于(%)", "threshold": 50, "enabled": False},
    ]

# ─── Student Profile ───
def get_student_profile(student_id: str):
    student = None
    for s in STUDENTS:
        if s["student_id"] == student_id:
            student = s
            break
    if not student:
        return None

    # Radar data: 5 dimensions
    radar = {
        "focus": round(random.uniform(60, 95), 1),
        "interaction": round(random.uniform(50, 90), 1),
        "discipline": round(random.uniform(70, 98), 1),
        "endurance": round(random.uniform(55, 90), 1),
        "attendance": round(random.uniform(85, 100), 1),
    }
    class_avg_radar = {
        "focus": 78.5,
        "interaction": 72.0,
        "discipline": 85.0,
        "endurance": 70.0,
        "attendance": 94.0,
    }

    # 30-day trend
    trend = []
    for i in range(29, -1, -1):
        d = datetime.now() - timedelta(days=i)
        trend.append({
            "date": d.strftime("%m-%d"),
            "score": round(random.uniform(60, 95), 1),
            "class_avg": round(random.uniform(70, 85), 1),
        })

    # Behavior stats
    behavior_stats = {
        "Listening": random.randint(300, 600),
        "Reading_Writing": random.randint(100, 300),
        "Sleeping": random.randint(10, 80),
        "Looking_Around": random.randint(20, 100),
        "Using_Phone": random.randint(0, 30),
        "Standing_Leaving": random.randint(0, 15),
    }

    # Recent records
    recent = []
    subjects = ["数据结构", "操作系统", "计算机网络", "计算机组成原理", "数据库原理", "软件工程"]
    for i in range(7):
        d = datetime.now() - timedelta(days=i)
        recent.append({
            "date": d.strftime("%Y-%m-%d"),
            "subject": random.choice(subjects),
            "focus_score": round(random.uniform(60, 95), 1),
            "main_behavior": random.choice(["专注听讲", "阅读/记笔记", "偶有走神"]),
        })

    return {
        "student_id": student["student_id"],
        "name": student["name"],
        "class_id": student["class_id"],
        "avatar": None,
        "attendance_rate": round(random.uniform(88, 100), 1),
        "avg_focus_score": round(random.uniform(70, 92), 1),
        "radar_data": {"student": radar, "class_avg": class_avg_radar},
        "trend_data": trend,
        "behavior_stats": behavior_stats,
        "recent_records": recent,
    }

# ─── Report Data (45-minute focus curve) ───
def get_report_data(schedule_id: int = 1):
    focus_curve = []
    base_score = 90
    for minute in range(46):
        if minute < 10:
            score = base_score + random.uniform(-3, 3)
        elif minute < 25:
            score = base_score - 2 + random.uniform(-5, 3)
        elif minute < 35:
            score = base_score - 12 + random.uniform(-8, 5)
        else:
            score = base_score - 20 + random.uniform(-10, 5)
        score = max(30, min(100, score))
        focus_curve.append({"minute": minute, "score": round(score, 1)})

    behavior_distribution = {
        "Listening": round(random.uniform(45, 60), 1),
        "Reading_Writing": round(random.uniform(15, 25), 1),
        "Sleeping": round(random.uniform(5, 12), 1),
        "Looking_Around": round(random.uniform(5, 10), 1),
        "Using_Phone": round(random.uniform(2, 8), 1),
        "Standing_Leaving": round(random.uniform(1, 5), 1),
    }

    heatmap = []
    behaviors = list(behavior_distribution.keys())
    for b_idx, behavior in enumerate(behaviors):
        for minute in range(0, 46, 5):
            val = random.randint(0, 15)
            heatmap.append([minute, b_idx, val])

    return {
        "schedule_id": schedule_id,
        "subject": "数据结构",
        "time_range": "14:00-14:45",
        "total_students": 45,
        "avg_focus": round(sum(p["score"] for p in focus_curve) / len(focus_curve), 1),
        "focus_curve": focus_curve,
        "behavior_distribution": behavior_distribution,
        "heatmap_data": heatmap,
        "heatmap_behaviors": ["听讲", "笔记", "趴桌", "左顾右盼", "玩手机", "起立离开"],
    }

# ─── System Settings (in-memory state) ───
_settings = {
    "current_model": "yolov11.pt",
    "confidence": 0.45,
    "iou": 0.5,
    "video_source": "class.mp4",
    "privacy_mode": False,
    "data_retention_days": 30,
    "auto_cleanup": True,
    "llm_api_url": "",
    "llm_api_key": "",
}

def get_settings():
    return dict(_settings)

def update_settings(new_settings: dict):
    _settings.update(new_settings)
    return dict(_settings)

# ─── System hardware metrics ───
def get_system_metrics():
    return {
        "cpu_percent": round(random.uniform(20, 65), 1),
        "gpu_percent": round(random.uniform(30, 80), 1),
        "memory_percent": round(random.uniform(40, 70), 1),
        "memory_used_gb": round(random.uniform(4, 12), 1),
        "memory_total_gb": 16.0,
        "fps": round(random.uniform(18, 30), 1),
        "uptime_hours": round(random.uniform(1, 72), 1),
    }
