from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId

# Input: Dữ liệu Frontend gửi lên khi tạo học sinh
class StudentCreate(BaseModel):
    name: str
    class_name: str # Frontend gửi field này là "class_name" hoặc "class" tùy bạn map
    nationality: str
    personality: Optional[str] = None
    interests: List[str] = []

# Input: Dữ liệu Frontend gửi lên khi cập nhật
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    personality: Optional[str] = None
    interests: Optional[List[str]] = None

# Output: Dữ liệu Backend trả về cho Frontend
class StudentResponse(BaseModel):
    id: PydanticObjectId 
    name: str
    class_name: str
    nationality: str
    # Các trường khác...
    
    class Config:
        # Cho phép map từ field 'class' trong DB sang 'class_name'
        populate_by_name = True