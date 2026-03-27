"""Student Profile API."""
from fastapi import APIRouter
from services.data_service import STUDENTS, get_student_profile

router = APIRouter(prefix="/api/v1/student", tags=["Student"])


@router.get("/list")
async def student_list(keyword: str = ""):
    """Get student list with optional search."""
    results = STUDENTS
    if keyword:
        results = [
            s for s in STUDENTS
            if keyword in s["name"] or keyword in s["student_id"]
        ]
    return {"code": 0, "data": results}


@router.get("/profile/{student_id}")
async def student_profile(student_id: str):
    """Get detailed student profile with radar/trend data."""
    profile = get_student_profile(student_id)
    if profile is None:
        return {"code": 404, "message": "Student not found", "data": None}
    return {"code": 0, "data": profile}
