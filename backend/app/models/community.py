from typing import List, Optional, Any, Literal
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

# --- Collection 7: Community Posts ---
class CommunityPost(Document):
    author_id: PydanticObjectId = Field(..., alias="authorId")
    title: str
    content: str
    excerpt: Optional[str] = None  # Short preview (auto-generated from content)
    tags: List[str] = []  # Tags instead of category (Reddit-style)
    upvotes: int = 0
    views: int = 0
    comment_count: int = Field(0, alias="commentCount")  # Cached comment count
    is_pinned: bool = Field(False, alias="isPinned")
    last_activity: datetime = Field(default_factory=datetime.now, alias="lastActivity")  # For "recently active" sort
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "community_posts"
    
    def generate_excerpt(self, max_length: int = 150) -> str:
        """Generate excerpt from content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length].rsplit(' ', 1)[0] + "..."


# --- Collection 8: Comments ---
class Comment(Document):
    post_id: PydanticObjectId = Field(..., alias="postId")
    author_id: PydanticObjectId = Field(..., alias="authorId")
    content: str
    upvotes: int = 0
    parent_comment_id: Optional[PydanticObjectId] = Field(None, alias="parentCommentId")
    depth: int = 0  # Nesting level (0 = root comment)
    is_deleted: bool = Field(False, alias="isDeleted")  # Soft delete flag
    deleted_by_admin: bool = Field(False, alias="deletedByAdmin")  # Flag if deleted by admin
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "comments"


# --- Collection 10: Upvotes (Track who voted what) ---
class Upvote(Document):
    user_id: PydanticObjectId = Field(..., alias="userId")
    target_type: Literal["post", "comment"] = Field(..., alias="targetType")
    target_id: PydanticObjectId = Field(..., alias="targetId")
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Settings:
        name = "upvotes"

# --- Collection 9: System Settings ---
class SystemSetting(Document):
    setting_type: str = Field(..., alias="settingType")
    key: str
    value: Any # Mixed type
    description: Optional[str] = None
    
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "system_settings"