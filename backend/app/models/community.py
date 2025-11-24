from typing import List, Optional, Any
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

# --- Collection 7: Community Posts ---
class CommunityPost(Document):
    author_id: PydanticObjectId = Field(..., alias="authorId")
    title: str
    content: str
    category: str # "advice", "experience", "question"
    tags: List[str] = []
    upvotes: int = 0
    views: int = 0
    is_pinned: bool = Field(False, alias="isPinned")
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "community_posts"

# --- Collection 8: Comments ---
class Comment(Document):
    post_id: PydanticObjectId = Field(..., alias="postId")
    author_id: PydanticObjectId = Field(..., alias="authorId")
    content: str
    upvotes: int = 0
    parent_comment_id: Optional[PydanticObjectId] = Field(None, alias="parentCommentId")
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "comments"

# --- Collection 9: System Settings ---
class SystemSetting(Document):
    setting_type: str = Field(..., alias="settingType")
    key: str
    value: Any # Mixed type
    description: Optional[str] = None
    
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "system_settings"