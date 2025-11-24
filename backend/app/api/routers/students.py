from fastapi import APIRouter, HTTPException
from typing import List
from app.models.education import Student # Import Model DB
from app.schemas.student import StudentCreate, StudentResponse # Import Schema

router = APIRouter()

# 1. API Tạo học sinh mới
@router.post("/", response_model=StudentResponse)
async def create_student(student_in: StudentCreate):
    # Tạo object Student từ dữ liệu gửi lên
    # Lưu ý: Tạm thời chúng ta hard-code teacher_id vì chưa làm chức năng Đăng nhập
    # Sau này sẽ lấy ID từ token của người đang đăng nhập
    new_student = Student(
        teacher_id="65f123456789abcdef123456", # ID giả định của giáo viên
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
async def get_students():
    students = await Student.find_all().to_list()
    return students