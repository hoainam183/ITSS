from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas.user import UserResponse, UserProfileUpdate, UserProfileResponse
from app.models.users import User
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information.
    Requires authentication (JWT token).
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        profile=UserProfileResponse(
            full_name=current_user.profile.full_name,
            school=current_user.profile.school,
            experience=current_user.profile.experience,
            avatar=current_user.profile.avatar
        ),
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile information.
    Requires authentication (JWT token).
    Only updates fields that are provided in the request.
    """
    # Update profile fields if provided
    if profile_update.full_name is not None:
        current_user.profile.full_name = profile_update.full_name
    
    if profile_update.school is not None:
        current_user.profile.school = profile_update.school
    
    if profile_update.experience is not None:
        current_user.profile.experience = profile_update.experience
    
    if profile_update.avatar is not None:
        current_user.profile.avatar = profile_update.avatar
    
    # Update timestamp
    current_user.updated_at = datetime.now()
    
    # Save to database
    await current_user.save()
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        profile=UserProfileResponse(
            full_name=current_user.profile.full_name,
            school=current_user.profile.school,
            experience=current_user.profile.experience,
            avatar=current_user.profile.avatar
        ),
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )
