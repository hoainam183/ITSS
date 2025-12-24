from typing import Optional, Union
from datetime import datetime
from beanie import Document
from pydantic import BaseModel, EmailStr, Field, field_validator

# Class con: Profile (Nhúng trong User)
class UserProfile(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    school: Optional[str] = None
    experience: Optional[str] = None # Kinh nghiệm và chuyên ngành (text mô tả)
    avatar: Optional[str] = None
    
    @field_validator('experience', mode='before')
    @classmethod
    def convert_experience_to_string(cls, v):
        """Convert int to string for backward compatibility with old data"""
        if v is None:
            return None
        if isinstance(v, int):
            return str(v)
        return v

# Collection 1: Users
class User(Document):
    username: str
    email: EmailStr
    password: str # Đã hash
    role: str = "teacher"  # "teacher" or "admin"
    profile: UserProfile = Field(default_factory=UserProfile)
    
    # Reset password fields
    reset_token: Optional[str] = Field(None, alias="resetToken")
    reset_token_expires: Optional[datetime] = Field(None, alias="resetTokenExpires")
    
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "users"