import { FiThumbsUp } from "react-icons/fi";
import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  fetchPost,
  fetchComments,
  fetchReplies,
  createComment,
  togglePostUpvote,
  toggleCommentUpvote,
  formatRelativeTime,
  type Post,
  type Comment,
} from "../services/communityApi";

// ============================================
// HELPER: Render content with clickable links
// ============================================
const renderWithLinks = (content: string): React.ReactNode => {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = content.split(urlRegex);

  return parts.map((part, index) => {
    if (part.match(urlRegex)) {
      return (
        <a
          key={index}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className="content-link"
        >
          {part.length > 50 ? part.slice(0, 50) + "..." : part}
        </a>
      );
    }
    return part;
  });
};

// ============================================
// COMMENT COMPONENT (recursive for replies)
// ============================================
interface CommentItemProps {
  comment: Comment;
  onReplySubmit: (parentId: string, content: string) => Promise<void>;
  onUpvote: (commentId: string) => Promise<void>;
  depth?: number;
}

const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  onReplySubmit,
  onUpvote,
  depth = 0,
}) => {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [showReplies, setShowReplies] = useState(false);
  const [replies, setReplies] = useState<Comment[]>([]);
  const [loadingReplies, setLoadingReplies] = useState(false);

  // Load replies when expanding
  const handleShowReplies = async () => {
    if (showReplies) {
      setShowReplies(false);
      return;
    }

    setLoadingReplies(true);
    try {
      const response = await fetchReplies(comment.id);
      setReplies(response.comments);
      setShowReplies(true);
    } catch {
      // Silently fail
    } finally {
      setLoadingReplies(false);
    }
  };

  // Submit reply
  const handleSubmitReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyContent.trim() || submitting) return;

    setSubmitting(true);
    try {
      await onReplySubmit(comment.id, replyContent.trim());
      setReplyContent("");
      setShowReplyForm(false);
      // Reload replies
      const response = await fetchReplies(comment.id);
      setReplies(response.comments);
      setShowReplies(true);
    } catch {
      // Handle error
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={`comment-item depth-${depth}`}>
      <div className="comment-main">
        {/* Vote */}
        <div className="comment-vote">
          <button
  className={`vote-btn-sm ${comment.userHasUpvoted ? "voted" : ""}`}
  onClick={() => onUpvote(comment.id)}
  title={comment.userHasUpvoted ? "いいねを取り消す" : "いいねする"}
>
  <FiThumbsUp />
</button>

          <span className="vote-count-sm">{comment.upvotes}</span>
        </div>

        {/* Content */}
        <div className="comment-body">
          <div className="comment-header">
            <span className="comment-author">
              {comment.author.fullName || comment.author.username}
            </span>
            <span className="comment-time">
              {formatRelativeTime(comment.createdAt)}
            </span>
          </div>

          <div className="comment-content">
            {renderWithLinks(comment.content)}
          </div>

          <div className="comment-actions">
            {/* Only show reply button for root comments (depth 0) */}
            {depth === 0 && (
              <button
                className="action-btn"
                onClick={() => setShowReplyForm(!showReplyForm)}
              >
                返信
              </button>
            )}

            {/* Show replies button */}
            {comment.replyCount > 0 && depth === 0 && (
              <button
                className="action-btn replies-btn"
                onClick={handleShowReplies}
              >
                {loadingReplies
                  ? "読み込み中..."
                  : showReplies
                  ? `返信を隠す`
                  : `${comment.replyCount}件の返信を表示`}
              </button>
            )}
          </div>

          {/* Inline Reply Form */}
          {showReplyForm && (
            <form className="reply-form" onSubmit={handleSubmitReply}>
              <textarea
                className="reply-input"
                placeholder="返信を入力..."
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                rows={2}
              />
              <div className="reply-actions">
                <button
                  type="button"
                  className="btn-cancel-sm"
                  onClick={() => setShowReplyForm(false)}
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  className="btn-submit-sm"
                  disabled={!replyContent.trim() || submitting}
                >
                  {submitting ? "送信中..." : "返信"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Nested Replies */}
      {showReplies && replies.length > 0 && (
        <div className="replies-container">
          {replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              onReplySubmit={onReplySubmit}
              onUpvote={onUpvote}
              depth={1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// MAIN PAGE COMPONENT
// ============================================
const PostDetailPage: React.FC = () => {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();

  // Post state
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Comments state
  const [comments, setComments] = useState<Comment[]>([]);
  const [loadingComments, setLoadingComments] = useState(false);

  // New comment state
  const [newComment, setNewComment] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);
  
  // Upvote loading states
  const [upvotingPost, setUpvotingPost] = useState(false);
  const [upvotingComments, setUpvotingComments] = useState<Set<string>>(new Set());

  // Load post
  const loadPost = useCallback(async () => {
    if (!postId) return;

    setLoading(true);
    setError(null);
    try {
      const postData = await fetchPost(postId);
      setPost(postData);
    } catch {
      setError("投稿が見つかりません。");
    } finally {
      setLoading(false);
    }
  }, [postId]);

  // Load comments
  const loadComments = useCallback(async () => {
    if (!postId) return;

    setLoadingComments(true);
    try {
      const response = await fetchComments(postId);
      setComments(response.comments);
    } catch {
      // Silently fail
    } finally {
      setLoadingComments(false);
    }
  }, [postId]);

  useEffect(() => {
    loadPost();
    loadComments();
  }, [loadPost, loadComments]);

  // Handle post upvote
  const handlePostUpvote = async () => {
    if (!post || upvotingPost) return;
    
    setUpvotingPost(true);
    try {
      const response = await togglePostUpvote(post.id);
      setPost((prev) =>
        prev
          ? {
              ...prev,
              upvotes: response.upvotes,
              userHasUpvoted: response.userHasUpvoted,
            }
          : null
      );
    } catch {
      // Silently fail
    } finally {
      setUpvotingPost(false);
    }
  };

  // Handle comment upvote
  const handleCommentUpvote = async (commentId: string) => {
    // Prevent double-click
    if (upvotingComments.has(commentId)) return;
    
    setUpvotingComments((prev) => new Set(prev).add(commentId));
    try {
      const response = await toggleCommentUpvote(commentId);
      // Update comment in list
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId
            ? {
                ...c,
                upvotes: response.upvotes,
                userHasUpvoted: response.userHasUpvoted,
              }
            : c
        )
      );
    } catch {
      // Silently fail
    } finally {
      setUpvotingComments((prev) => {
        const next = new Set(prev);
        next.delete(commentId);
        return next;
      });
    }
  };

  // Handle new comment submit
  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postId || !newComment.trim() || submittingComment) return;

    setSubmittingComment(true);
    try {
      await createComment(postId, newComment.trim());
      setNewComment("");
      // Reload comments
      loadComments();
      // Update comment count
      setPost((prev) =>
        prev ? { ...prev, commentCount: prev.commentCount + 1 } : null
      );
    } catch {
      setError("コメントの投稿に失敗しました。");
    } finally {
      setSubmittingComment(false);
    }
  };

  // Handle reply submit
  const handleReplySubmit = async (parentId: string, content: string) => {
    if (!postId) return;
    await createComment(postId, content, parentId);
    // Update comment count
    setPost((prev) =>
      prev ? { ...prev, commentCount: prev.commentCount + 1 } : null
    );
  };

  // Loading state
  if (loading) {
    return (
      <div className="post-detail-page">
        <div className="loading-message">読み込み中...</div>
      </div>
    );
  }

  // Error state
  if (error || !post) {
    return (
      <div className="post-detail-page">
        <div className="error-container">
          <p>{error || "投稿が見つかりません。"}</p>
          <button className="btn-back" onClick={() => navigate("/community")}>
            掲示板に戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="post-detail-page">
      {/* Back Link */}
      <Link to="/community" className="back-link">
        ← 掲示板に戻る
      </Link>

      {/* Post Card */}
      <article className="post-detail-card">
        {/* Vote Section */}
        <div className="post-detail-vote">
  <button
    className={`vote-btn-lg ${post.userHasUpvoted ? "voted" : ""}`}
    onClick={handlePostUpvote}
    disabled={upvotingPost}
    title={post.userHasUpvoted ? "いいねを取り消す" : "いいねする"}
  >
    <FiThumbsUp />
  </button>
  <span className="vote-count-lg">{post.upvotes}</span>
</div>


        {/* Content Section */}
        <div className="post-detail-content">
          {/* Header */}
          <div className="post-detail-header">
            {post.isPinned && <span className="pinned-badge">📌 固定</span>}
            <h1 className="post-detail-title">{post.title}</h1>
          </div>

          {/* Meta */}
          <div className="post-detail-meta">
            <span className="author">
              {post.author.fullName || post.author.username}
            </span>
            <span className="time">{formatRelativeTime(post.createdAt)}</span>
            <span className="stats">
              👁 {post.views} · 💬 {post.commentCount}
            </span>
          </div>

          {/* Tags */}
          {post.tags.length > 0 && (
            <div className="post-detail-tags">
              {post.tags.map((tag) => (
                <Link
                  key={tag}
                  to={`/community?tags=${tag}`}
                  className="detail-tag"
                >
                  {tag}
                </Link>
              ))}
            </div>
          )}

          {/* Body */}
          <div className="post-detail-body">
            {post.content.split("\n").map((paragraph, idx) => (
              <p key={idx}>{renderWithLinks(paragraph)}</p>
            ))}
          </div>
        </div>
      </article>

      {/* Comments Section */}
      <section className="comments-section">
        <h2 className="comments-title">
          コメント ({post.commentCount})
        </h2>

        {/* New Comment Form */}
        <form className="new-comment-form" onSubmit={handleSubmitComment}>
          <textarea
            className="comment-textarea"
            placeholder="コメントを入力..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            rows={3}
          />
          <button
            type="submit"
            className="btn-comment"
            disabled={!newComment.trim() || submittingComment}
          >
            {submittingComment ? "送信中..." : "コメントを投稿"}
          </button>
        </form>

        {/* Comments List */}
        <div className="comments-list">
          {loadingComments ? (
            <div className="loading-message">コメントを読み込み中...</div>
          ) : comments.length === 0 ? (
            <div className="no-comments">
              まだコメントがありません。最初のコメントを投稿しましょう！
            </div>
          ) : (
            comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                onReplySubmit={handleReplySubmit}
                onUpvote={handleCommentUpvote}
              />
            ))
          )}
        </div>
      </section>
    </div>
  );
};

export default PostDetailPage;

