/**
 * Community Board API Service
 * Connects to backend /community endpoints
 */

const API_BASE = "http://localhost:8000/community";

// ============================================
// TYPES
// ============================================

export interface Author {
  id: string;
  username: string;
  fullName: string | null;
}

export interface Post {
  id: string;
  author: Author;
  title: string;
  content: string;
  excerpt: string | null;
  tags: string[];
  upvotes: number;
  views: number;
  commentCount: number;
  isPinned: boolean;
  userHasUpvoted: boolean;
  lastActivity: string;
  createdAt: string;
  updatedAt: string;
}

export interface PostListItem {
  id: string;
  author: Author;
  title: string;
  excerpt: string | null;
  tags: string[];
  upvotes: number;
  views: number;
  commentCount: number;
  isPinned: boolean;
  userHasUpvoted: boolean;
  createdAt: string;
}

export interface PostListResponse {
  posts: PostListItem[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface TagInfo {
  name: string;
  count: number;
}

export interface UpvoteResponse {
  success: boolean;
  upvotes: number;
  userHasUpvoted: boolean;
}

export interface Comment {
  id: string;
  postId: string;
  author: Author;
  content: string;
  upvotes: number;
  parentCommentId: string | null;
  depth: number;
  userHasUpvoted: boolean;
  replyCount: number;
  replies: Comment[];
  createdAt: string;
  updatedAt: string;
}

export interface CommentListResponse {
  comments: Comment[];
  total: number;
}

// ============================================
// API ERROR
// ============================================

export class ApiError extends Error {
  public status: number;
  public retryable: boolean;

  constructor(message: string, status: number, retryable: boolean = false) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryable = retryable;
  }
}

// ============================================
// POST APIs
// ============================================

export type SortOption = "newest" | "upvotes" | "views" | "active";

export interface FetchPostsParams {
  q?: string;
  tags?: string[];
  sort?: SortOption;
  page?: number;
  limit?: number;
}

/**
 * Fetch posts with search, filter, sort, pagination
 */
export async function fetchPosts(params: FetchPostsParams = {}): Promise<PostListResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.q) searchParams.set("q", params.q);
  if (params.tags && params.tags.length > 0) {
    searchParams.set("tags", params.tags.join(","));
  }
  if (params.sort) searchParams.set("sort", params.sort);
  if (params.page) searchParams.set("page", params.page.toString());
  if (params.limit) searchParams.set("limit", params.limit.toString());
  
  const url = `${API_BASE}/posts?${searchParams.toString()}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new ApiError("投稿の取得に失敗しました", response.status, true);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Fetch single post detail
 */
export async function fetchPost(postId: string): Promise<Post> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}`);
    if (!response.ok) {
      throw new ApiError("投稿が見つかりません", response.status, false);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Create new post
 */
export async function createPost(data: {
  title: string;
  content: string;
  tags: string[];
}): Promise<Post> {
  try {
    const response = await fetch(`${API_BASE}/posts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || "投稿の作成に失敗しました",
        response.status,
        false
      );
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Update post
 */
export async function updatePost(
  postId: string,
  data: { title?: string; content?: string; tags?: string[] }
): Promise<Post> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new ApiError("投稿の更新に失敗しました", response.status, false);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Delete post
 */
export async function deletePost(postId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new ApiError("投稿の削除に失敗しました", response.status, false);
    }
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Toggle upvote on post
 */
export async function togglePostUpvote(postId: string): Promise<UpvoteResponse> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}/upvote`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new ApiError("投票に失敗しました", response.status, true);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

// ============================================
// TAG APIs
// ============================================

/**
 * Fetch popular tags
 */
export async function fetchTags(limit: number = 20): Promise<TagInfo[]> {
  try {
    const response = await fetch(`${API_BASE}/tags?limit=${limit}`);
    if (!response.ok) {
      throw new ApiError("タグの取得に失敗しました", response.status, true);
    }
    const data = await response.json();
    return data.tags;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

// ============================================
// COMMENT APIs
// ============================================

/**
 * Fetch comments for a post (root comments only)
 */
export async function fetchComments(postId: string): Promise<CommentListResponse> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}/comments`);
    if (!response.ok) {
      throw new ApiError("コメントの取得に失敗しました", response.status, true);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Fetch replies for a comment
 */
export async function fetchReplies(commentId: string): Promise<CommentListResponse> {
  try {
    const response = await fetch(`${API_BASE}/comments/${commentId}/replies`);
    if (!response.ok) {
      throw new ApiError("返信の取得に失敗しました", response.status, true);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Create comment
 */
export async function createComment(
  postId: string,
  content: string,
  parentCommentId?: string
): Promise<Comment> {
  try {
    const response = await fetch(`${API_BASE}/posts/${postId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, parentCommentId }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || "コメントの投稿に失敗しました",
        response.status,
        false
      );
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Toggle upvote on comment
 */
export async function toggleCommentUpvote(commentId: string): Promise<UpvoteResponse> {
  try {
    const response = await fetch(`${API_BASE}/comments/${commentId}/upvote`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new ApiError("投票に失敗しました", response.status, true);
    }
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

// ============================================
// UTILITIES
// ============================================

/**
 * Format date to relative time (e.g., "2時間前")
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  const diffWeek = Math.floor(diffDay / 7);
  const diffMonth = Math.floor(diffDay / 30);

  if (diffMin < 1) return "たった今";
  if (diffMin < 60) return `${diffMin}分前`;
  if (diffHour < 24) return `${diffHour}時間前`;
  if (diffDay < 7) return `${diffDay}日前`;
  if (diffWeek < 4) return `${diffWeek}週間前`;
  if (diffMonth < 12) return `${diffMonth}ヶ月前`;
  return date.toLocaleDateString("ja-JP");
}

/**
 * Render content with clickable URLs
 */
export function renderContentWithLinks(content: string): string {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
}

