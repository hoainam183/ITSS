"""
Pydantic schemas for Community Board feature
- Posts: CRUD, Search, Filter, Pagination
- Comments: CRUD, Nested replies
- Upvotes: Track user votes
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================
# AUTHOR INFO (embedded in responses)
# ============================================

class AuthorInfo(BaseModel):
    """Author information for posts and comments"""
    id: str
    username: str
    full_name: Optional[str] = Field(None, alias="fullName")

    class Config:
        populate_by_name = True


# ============================================
# POST SCHEMAS
# ============================================

class PostCreateRequest(BaseModel):
    """Request to create a new post"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    tags: List[str] = Field(default=[], max_length=10)


class PostUpdateRequest(BaseModel):
    """Request to update a post"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    tags: Optional[List[str]] = Field(None, max_length=10)


class PostResponse(BaseModel):
    """Response for a single post"""
    id: str
    author: AuthorInfo
    title: str
    content: str
    excerpt: Optional[str] = None
    tags: List[str] = []
    upvotes: int = 0
    views: int = 0
    comment_count: int = Field(0, alias="commentCount")
    is_pinned: bool = Field(False, alias="isPinned")
    user_has_upvoted: bool = Field(False, alias="userHasUpvoted")
    last_activity: datetime = Field(alias="lastActivity")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class PostListItem(BaseModel):
    """Simplified post for list view"""
    id: str
    author: AuthorInfo
    title: str
    excerpt: Optional[str] = None
    tags: List[str] = []
    upvotes: int = 0
    views: int = 0
    comment_count: int = Field(0, alias="commentCount")
    is_pinned: bool = Field(False, alias="isPinned")
    user_has_upvoted: bool = Field(False, alias="userHasUpvoted")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class PostListResponse(BaseModel):
    """Paginated list of posts"""
    posts: List[PostListItem]
    total: int
    page: int
    limit: int
    total_pages: int = Field(alias="totalPages")
    has_next: bool = Field(alias="hasNext")
    has_prev: bool = Field(alias="hasPrev")

    class Config:
        populate_by_name = True


# ============================================
# COMMENT SCHEMAS
# ============================================

class CommentCreateRequest(BaseModel):
    """Request to create a comment"""
    content: str = Field(..., min_length=1, max_length=5000)
    parent_comment_id: Optional[str] = Field(None, alias="parentCommentId")

    class Config:
        populate_by_name = True


class CommentUpdateRequest(BaseModel):
    """Request to update a comment"""
    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Response for a single comment (root comment)"""
    id: str
    post_id: str = Field(alias="postId")
    author: AuthorInfo
    content: str
    upvotes: int = 0
    parent_comment_id: Optional[str] = Field(None, alias="parentCommentId")
    depth: int = 0
    user_has_upvoted: bool = Field(False, alias="userHasUpvoted")
    reply_count: int = Field(0, alias="replyCount")  # Number of replies
    replies: List["CommentResponse"] = []  # Only populated when expanded
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class CommentListResponse(BaseModel):
    """List of root comments for a post (replies loaded separately)"""
    comments: List[CommentResponse]
    total: int  # Total root comments


# ============================================
# UPVOTE SCHEMAS
# ============================================

class UpvoteResponse(BaseModel):
    """Response after upvote/remove upvote"""
    success: bool
    upvotes: int  # New upvote count
    user_has_upvoted: bool = Field(alias="userHasUpvoted")

    class Config:
        populate_by_name = True


# ============================================
# SEARCH & FILTER SCHEMAS
# ============================================

class SearchParams(BaseModel):
    """Search and filter parameters"""
    q: Optional[str] = None  # Search query
    tags: Optional[List[str]] = None  # Filter by tags
    sort: Literal["newest", "upvotes", "views", "active"] = "newest"
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=50)


# ============================================
# TAG SCHEMAS
# ============================================

class TagInfo(BaseModel):
    """Tag with usage count"""
    name: str
    count: int


class TagListResponse(BaseModel):
    """List of popular tags"""
    tags: List[TagInfo]


# ============================================
# PINNED POST SCHEMAS
# ============================================

class PinPostRequest(BaseModel):
    """Request to pin/unpin a post"""
    is_pinned: bool = Field(alias="isPinned")

    class Config:
        populate_by_name = True
