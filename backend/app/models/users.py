from typing import Optional
from datetime import datetime
from beanie import Document
from pydantic import BaseModel, EmailStr, Field

# Class con: Profile (Nhúng trong User)
class UserProfile(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    school: Optional[str] = None
    experience: Optional[int] = None # Số năm kinh nghiệm
    avatar: Optional[str] = None

# Collection 1: Users
class User(Document):
    username: str
    email: EmailStr
    password: str # Đã hash
    profile: UserProfile = Field(default_factory=UserProfile)
    
    # Reset password fields
    reset_token: Optional[str] = Field(None, alias="resetToken")
    reset_token_expires: Optional[datetime] = Field(None, alias="resetTokenExpires")
    
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "users"