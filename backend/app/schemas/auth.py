from pydantic import BaseModel, EmailStr, Field, field_validator


# Register Request
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = Field(None, alias="fullName")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


# Login Request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Token Response
class TokenResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    
    class Config:
        populate_by_name = True


# Forgot Password Request
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Reset Password Request
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, alias="newPassword")
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
