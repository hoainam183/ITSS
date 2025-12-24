"""
Community Board API Router
- Posts: CRUD, Search, Filter, Pagination, Sort
- Pinned posts support
- View count tracking
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
import math

from app.models.community import CommunityPost, Comment, Upvote
from app.models.users import User
from app.core.deps import get_current_user
from app.schemas.community import (
    PostCreateRequest,
    PostUpdateRequest,
    PostResponse,
    PostListItem,
    PostListResponse,
    AuthorInfo,
    TagInfo,
    TagListResponse,
    PinPostRequest,
    UpvoteResponse,
    CommentCreateRequest,
    CommentUpdateRequest,
    CommentResponse,
    CommentListResponse,
)

router = APIRouter(prefix="/community", tags=["Community Board"])


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_author_info(author_id: PydanticObjectId) -> AuthorInfo:
    """Get author info from user ID"""
    user = await User.get(author_id)
    if not user:
        return AuthorInfo(id=str(author_id), username="Unknown", fullName="Unknown User")
    
    return AuthorInfo(
        id=str(user.id),
        username=user.username,
        fullName=user.profile.full_name if user.profile else user.username,
    )


# ============================================
# POST ENDPOINTS
# ============================================

@router.get("/posts", response_model=PostListResponse)
async def get_posts(
    q: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    sort: str = Query("newest", description="Sort: newest, upvotes, views, active"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of posts with search, filter, pagination, and sorting.
    Pinned posts always appear first.
    """
    current_user_id = current_user.id
    
    # Build query filters
    filters = {}
    
    # Search by title or content
    if q:
        filters["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]
    
    # Filter by tags
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            filters["tags"] = {"$in": tag_list}
    
    # Determine sort field
    sort_map = {
    "newest": [("createdAt", -1)],
    "upvotes": [("upvotes", -1), ("createdAt", -1)],
    "views": [("views", -1), ("createdAt", -1)],
    "active": [("last_activity", -1)],
}

    sort_fields = sort_map.get(sort, sort_map["newest"])

    final_sort = [("is_pinned", -1)] + sort_fields
    
    # Query with pagination
    skip = (page - 1) * limit
    
    # Get total count
    total = await CommunityPost.find(filters).count()
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get posts with sorting (pinned first, then by sort criteria)
    posts = await CommunityPost.find(filters) \
    .sort(final_sort) \
    .skip(skip) \
    .limit(limit) \
    .to_list()
    
    # Get user's upvotes for these posts
    post_ids = [post.id for post in posts]
    user_upvotes = await Upvote.find({
        "userId": current_user_id,
        "targetType": "post",
        "targetId": {"$in": post_ids}
    }).to_list()
    upvoted_post_ids = {str(u.target_id) for u in user_upvotes}
    
    # Build response
    post_items = []
    for post in posts:
        author = await get_author_info(post.author_id)
        post_items.append(PostListItem(
            id=str(post.id),
            author=author,
            title=post.title,
            excerpt=post.excerpt or post.generate_excerpt(),
            tags=post.tags,
            upvotes=post.upvotes,
            views=post.views,
            commentCount=post.comment_count,
            isPinned=post.is_pinned,
            userHasUpvoted=str(post.id) in upvoted_post_ids,
            createdAt=post.created_at,
        ))
    
    return PostListResponse(
        posts=post_items,
        total=total,
        page=page,
        limit=limit,
        totalPages=total_pages,
        hasNext=page < total_pages,
        hasPrev=page > 1,
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get single post detail. Increments view count.
    """
    current_user_id = current_user.id
    
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post.views += 1
    await post.save()
    
    # Check if user has upvoted
    user_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "post",
        "targetId": post.id
    })
    
    author = await get_author_info(post.author_id)
    
    return PostResponse(
        id=str(post.id),
        author=author,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        tags=post.tags,
        upvotes=post.upvotes,
        views=post.views,
        commentCount=post.comment_count,
        isPinned=post.is_pinned,
        userHasUpvoted=user_upvote is not None,
        lastActivity=post.last_activity,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    request: PostCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post.
    """
    current_user_id = current_user.id
    
    # Create post
    post = CommunityPost(
        author_id=current_user_id,
        title=request.title,
        content=request.content,
        tags=[tag.lower().strip() for tag in request.tags],
        last_activity=datetime.now(),
    )
    
    # Generate excerpt
    post.excerpt = post.generate_excerpt()
    
    await post.insert()
    
    author = await get_author_info(current_user_id)
    
    return PostResponse(
        id=str(post.id),
        author=author,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        tags=post.tags,
        upvotes=0,
        views=0,
        commentCount=0,
        isPinned=False,
        userHasUpvoted=False,
        lastActivity=post.last_activity,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    request: PostUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update a post (only by author).
    """
    current_user_id = current_user.id
    
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check ownership
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    
    # Update fields
    if request.title is not None:
        post.title = request.title
    if request.content is not None:
        post.content = request.content
        post.excerpt = post.generate_excerpt()
    if request.tags is not None:
        post.tags = [tag.lower().strip() for tag in request.tags]
    
    post.updated_at = datetime.now()
    await post.save()
    
    # Check if user has upvoted
    user_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "post",
        "targetId": post.id
    })
    
    author = await get_author_info(post.author_id)
    
    return PostResponse(
        id=str(post.id),
        author=author,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        tags=post.tags,
        upvotes=post.upvotes,
        views=post.views,
        commentCount=post.comment_count,
        isPinned=post.is_pinned,
        userHasUpvoted=user_upvote is not None,
        lastActivity=post.last_activity,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a post (only by author). Also deletes all comments and upvotes.
    """
    current_user_id = current_user.id
    
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check ownership
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    # Delete related comments
    await Comment.find({"postId": post.id}).delete()
    
    # Delete related upvotes
    await Upvote.find({
        "targetType": "post",
        "targetId": post.id
    }).delete()
    
    # Delete post
    await post.delete()
    
    return None


# ============================================
# UPVOTE ENDPOINTS
# ============================================

@router.post("/posts/{post_id}/upvote", response_model=UpvoteResponse)
async def upvote_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Upvote a post. If already upvoted, removes the upvote (toggle).
    """
    current_user_id = current_user.id
    
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check existing upvote
    existing_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "post",
        "targetId": post.id
    })
    
    if existing_upvote:
        # Remove upvote
        await existing_upvote.delete()
        post.upvotes = max(0, post.upvotes - 1)
        await post.save()
        return UpvoteResponse(success=True, upvotes=post.upvotes, userHasUpvoted=False)
    else:
        # Add upvote
        upvote = Upvote(
            user_id=current_user_id,
            target_type="post",
            target_id=post.id
        )
        await upvote.insert()
        post.upvotes += 1
        await post.save()
        return UpvoteResponse(success=True, upvotes=post.upvotes, userHasUpvoted=True)


# ============================================
# PIN ENDPOINTS
# ============================================

@router.put("/posts/{post_id}/pin", response_model=PostResponse)
async def pin_post(
    post_id: str,
    request: PinPostRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Pin or unpin a post (admin only).
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can pin/unpin posts"
        )
    
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.is_pinned = request.is_pinned
    post.updated_at = datetime.now()
    await post.save()
    
    current_user_id = current_user.id
    user_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "post",
        "targetId": post.id
    })
    
    author = await get_author_info(post.author_id)
    
    return PostResponse(
        id=str(post.id),
        author=author,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        tags=post.tags,
        upvotes=post.upvotes,
        views=post.views,
        commentCount=post.comment_count,
        isPinned=post.is_pinned,
        userHasUpvoted=user_upvote is not None,
        lastActivity=post.last_activity,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


# ============================================
# TAGS ENDPOINTS
# ============================================

@router.get("/tags", response_model=TagListResponse)
async def get_popular_tags(limit: int = Query(20, ge=1, le=50)):
    """
    Get popular tags with usage count.
    Workaround: Using Python counting instead of MongoDB aggregation
    due to Beanie 2.0.x + Motor 3.7.x compatibility issue.
    """
    from collections import Counter
    
    # Fetch all posts (only tags field needed)
    posts = await CommunityPost.find_all().to_list()
    
    # Count tags using Python Counter
    tag_counter: Counter[str] = Counter()
    for post in posts:
        for tag in post.tags:
            tag_counter[tag] += 1
    
    # Get most common tags
    most_common = tag_counter.most_common(limit)
    tags = [TagInfo(name=tag, count=count) for tag, count in most_common]
    
    return TagListResponse(tags=tags)


# ============================================
# COMMENTS ENDPOINTS
# ============================================

async def build_comment_response(
    comment: Comment, 
    current_user_id: PydanticObjectId,
    include_replies: bool = False
) -> CommentResponse:
    """Build CommentResponse with author info and optional replies"""
    author = await get_author_info(comment.author_id)
    
    # Check if user has upvoted
    user_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "comment",
        "targetId": comment.id
    })
    
    # Count replies
    reply_count = await Comment.find({
        "parentCommentId": comment.id
    }).count()
    
    # Load replies if requested
    replies = []
    if include_replies and reply_count > 0:
        reply_docs = await Comment.find({
            "parentCommentId": comment.id
        }).sort("createdAt").to_list()
        
        for reply in reply_docs:
            reply_response = await build_comment_response(reply, current_user_id, False)
            replies.append(reply_response)
    
    return CommentResponse(
        id=str(comment.id),
        postId=str(comment.post_id),
        author=author,
        content=comment.content if not comment.is_deleted else "",  # Empty content if deleted
        upvotes=comment.upvotes,
        parentCommentId=str(comment.parent_comment_id) if comment.parent_comment_id else None,
        depth=comment.depth,
        userHasUpvoted=user_upvote is not None,
        replyCount=reply_count,
        replies=replies,
        isDeleted=comment.is_deleted,
        deletedByAdmin=comment.deleted_by_admin,
        createdAt=comment.created_at,
        updatedAt=comment.updated_at,
    )


@router.get("/posts/{post_id}/comments", response_model=CommentListResponse)
async def get_post_comments(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get root comments for a post (depth=0).
    Replies are not loaded by default - use GET /comments/{id}/replies.
    Sort: oldest first.
    """
    current_user_id = current_user.id
    
    # Verify post exists
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get root comments only (parent_comment_id is None)
    root_comments = await Comment.find({
        "postId": post.id,
        "parentCommentId": None
    }).sort("createdAt").to_list()
    
    # Build response
    comments = []
    for comment in root_comments:
        comment_response = await build_comment_response(comment, current_user_id, False)
        comments.append(comment_response)
    
    return CommentListResponse(
        comments=comments,
        total=len(root_comments)
    )


@router.get("/comments/{comment_id}/replies", response_model=CommentListResponse)
async def get_comment_replies(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all replies for a comment (load all at once - YouTube style).
    """
    current_user_id = current_user.id
    
    try:
        parent_comment = await Comment.get(PydanticObjectId(comment_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Get all replies (depth=1 only, no further nesting)
    replies = await Comment.find({
        "parentCommentId": parent_comment.id
    }).sort("createdAt").to_list()
    
    # Build response
    reply_responses = []
    for reply in replies:
        reply_response = await build_comment_response(reply, current_user_id, False)
        reply_responses.append(reply_response)
    
    return CommentListResponse(
        comments=reply_responses,
        total=len(reply_responses)
    )


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: str,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a comment on a post.
    - If parentCommentId is null: creates root comment (depth=0)
    - If parentCommentId is set: creates reply (depth=1, max 2 levels)
    """
    current_user_id = current_user.id
    
    # Verify post exists
    try:
        post = await CommunityPost.get(PydanticObjectId(post_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Determine depth and validate parent
    depth = 0
    parent_comment_id = None
    
    if request.parent_comment_id:
        try:
            parent_comment = await Comment.get(PydanticObjectId(request.parent_comment_id))
        except Exception:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        # Max 2 levels - if parent is already a reply (depth=1), reject
        if parent_comment.depth >= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot reply to a reply. Max depth is 2 levels."
            )
        
        depth = 1
        parent_comment_id = parent_comment.id
    
    # Create comment
    comment = Comment(
        post_id=post.id,
        author_id=current_user_id,
        content=request.content,
        parent_comment_id=parent_comment_id,
        depth=depth,
    )
    await comment.insert()
    
    # Update post's comment_count and last_activity
    post.comment_count += 1
    post.last_activity = datetime.now()
    await post.save()
    
    return await build_comment_response(comment, current_user_id, False)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    request: CommentUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment (only by author).
    """
    current_user_id = current_user.id
    
    try:
        comment = await Comment.get(PydanticObjectId(comment_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check ownership
    if comment.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")
    
    # Update content
    comment.content = request.content
    comment.updated_at = datetime.now()
    await comment.save()
    
    return await build_comment_response(comment, current_user_id, False)


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a comment.
    - Author can delete their own comments
    - Admin can delete any comment
    - If deleting root comment: also soft delete all its replies
    - If deleting reply: only soft delete that reply
    Marks comment as deleted but keeps it in database for display as "comment deleted".
    """
    current_user_id = current_user.id
    is_admin = current_user.role == "admin"
    
    try:
        comment = await Comment.get(PydanticObjectId(comment_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check ownership (unless admin)
    if not is_admin and comment.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    # Check if already deleted
    if comment.is_deleted:
        raise HTTPException(status_code=400, detail="Comment is already deleted")
    
    # Check if this is a root comment (no parent) or a reply
    is_root_comment = comment.parent_comment_id is None
    
    if is_root_comment:
        # If deleting root comment: soft delete all replies
        replies = await Comment.find({
            "parentCommentId": comment.id,
            "isDeleted": False  # Only delete replies that aren't already deleted
        }).to_list()
        
        # Soft delete all replies (mark as deleted by admin if admin is deleting)
        for reply in replies:
            reply.is_deleted = True
            reply.deleted_by_admin = is_admin
            reply.updated_at = datetime.now()
            await reply.save()
    
    # Soft delete the comment itself
    comment.is_deleted = True
    comment.deleted_by_admin = is_admin
    comment.updated_at = datetime.now()
    await comment.save()
    
    return None


# ============================================
# COMMENT UPVOTE ENDPOINTS
# ============================================

@router.post("/comments/{comment_id}/upvote", response_model=UpvoteResponse)
async def upvote_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Upvote a comment. If already upvoted, removes the upvote (toggle).
    """
    current_user_id = current_user.id
    
    try:
        comment = await Comment.get(PydanticObjectId(comment_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check existing upvote
    existing_upvote = await Upvote.find_one({
        "userId": current_user_id,
        "targetType": "comment",
        "targetId": comment.id
    })
    
    if existing_upvote:
        # Remove upvote
        await existing_upvote.delete()
        comment.upvotes = max(0, comment.upvotes - 1)
        await comment.save()
        return UpvoteResponse(success=True, upvotes=comment.upvotes, userHasUpvoted=False)
    else:
        # Add upvote
        upvote = Upvote(
            user_id=current_user_id,
            target_type="comment",
            target_id=comment.id
        )
        await upvote.insert()
        comment.upvotes += 1
        await comment.save()
        return UpvoteResponse(success=True, upvotes=comment.upvotes, userHasUpvoted=True)
