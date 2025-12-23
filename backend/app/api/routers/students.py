from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.education import Student # Import Model DB
from app.models.users import User
from app.schemas.student import StudentCreate, StudentResponse # Import Schema
from app.core.deps import get_current_user

router = APIRouter()

# 1. API Tạo học sinh mới
@router.post("/", response_model=StudentResponse)
async def create_student(
    student_in: StudentCreate,
    current_user: User = Depends(get_current_user)
):
    # Tạo object Student từ dữ liệu gửi lên
    # Lấy teacher_id từ user đang đăng nhập
    new_student = Student(
        teacher_id=current_user.id,
        name=student_in.name,
        class_name=student_in.class_name, # Map schema -> model
        nationality=student_in.nationality,
        personality=student_in.personality,
        interests=student_in.interests
    )
    
    # Lưu vào DB
    await new_student.insert()
    return new_student

# 2. API Lấy danh sách tất cả học sinh
@router.get("/", response_model=List[StudentResponse])
async def get_students(current_user: User = Depends(get_current_user)):
    # Chỉ lấy học sinh của giáo viên hiện tại
    students = await Student.find(Student.teacher_id == current_user.id).to_list()
    return students