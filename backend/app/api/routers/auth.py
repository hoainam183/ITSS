from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
import secrets
import string
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.models.users import User, UserProfile
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.email_service import send_reset_password_email

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    - Validates email is not already registered
    - Hashes password
    - Creates user in database
    - Returns JWT access token
    """
    # Check if email already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await User.find_one(User.username == request.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user profile
    profile = UserProfile()
    if request.full_name:
        profile.full_name = request.full_name
    
    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        password=get_password_hash(request.password),
        profile=profile,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    await new_user.insert()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    - Verifies credentials
    - Updates last_login timestamp
    - Returns JWT access token
    """
    # Find user by email
    user = await User.find_one(User.email == request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
    # Verify password
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
    # Update last login
    user.last_login = datetime.now()
    await user.save()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset.
    - Generates reset token
    - Saves token to database with 1-hour expiry
    - Sends reset email to user
    """
    # Find user by email
    user = await User.find_one(User.email == request.email)
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token (8-digit alphanumeric)
    reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    # Set token expiry (1 hour from now)
    token_expires = datetime.now() + timedelta(hours=1)
    
    # Save token to user
    user.reset_token = reset_token
    user.reset_token_expires = token_expires
    await user.save()
    
    # Send email
    await send_reset_password_email(user.email, reset_token)
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using token.
    - Verifies reset token is valid and not expired
    - Updates password
    - Clears reset token
    """
    # Find user by reset token
    user = await User.find_one(User.reset_token == request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if not user.reset_token_expires or user.reset_token_expires < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.updated_at = datetime.now()
    await user.save()
    
    return {"message": "Password reset successfully"}
