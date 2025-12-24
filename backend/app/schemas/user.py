from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId


# User Profile Response
class UserProfileResponse(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    school: Optional[str] = None
    experience: Optional[str] = None
    avatar: Optional[str] = None


# User Response (for GET /users/me)
class UserResponse(BaseModel):
    id: PydanticObjectId
    username: str
    email: EmailStr
    profile: UserProfileResponse
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        populate_by_name = True


# User Profile Update Request
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    school: Optional[str] = None
    experience: Optional[str] = None
    avatar: Optional[str] = None
