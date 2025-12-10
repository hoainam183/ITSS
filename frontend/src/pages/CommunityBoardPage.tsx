import { FiThumbsUp } from "react-icons/fi";
import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  fetchPosts,
  fetchTags,
  createPost,
  togglePostUpvote,
  formatRelativeTime,
  type PostListItem,
  type TagInfo,
  type SortOption,
} from "../services/communityApi";

const CommunityBoardPage: React.FC = () => {
  // Posts state
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortOption, setSortOption] = useState<SortOption>("newest");

  // Tags state
  const [availableTags, setAvailableTags] = useState<TagInfo[]>([]);

  // Create post state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPostTitle, setNewPostTitle] = useState("");
  const [newPostContent, setNewPostContent] = useState("");
  const [newPostTags, setNewPostTags] = useState("");
  const [creating, setCreating] = useState(false);
  
  // Upvote loading state (track which posts are being upvoted)
  const [upvotingPosts, setUpvotingPosts] = useState<Set<string>>(new Set());

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1); // Reset to page 1 on search
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load posts
  const loadPosts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchPosts({
        q: debouncedSearch || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        sort: sortOption,
        page,
        limit: 10,
      });
      setPosts(response.posts);
      setTotalPages(response.totalPages);
      setTotal(response.total);
    } catch (err) {
      setError("投稿の読み込みに失敗しました。");
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, selectedTags, sortOption, page]);

  // Load tags
  const loadTags = useCallback(async () => {
    try {
      const tags = await fetchTags(15);
      setAvailableTags(tags);
    } catch {
      // Silently fail for tags
    }
  }, []);

  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  useEffect(() => {
    loadTags();
  }, [loadTags]);

  // Handle tag click
  const handleTagClick = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
    setPage(1);
  };

  // Handle sort change
  const handleSortChange = (sort: SortOption) => {
    setSortOption(sort);
    setPage(1);
  };

  // Handle upvote
  const handleUpvote = async (postId: string) => {
    // Prevent double-click
    if (upvotingPosts.has(postId)) return;
    
    setUpvotingPosts((prev) => new Set(prev).add(postId));
    try {
      const response = await togglePostUpvote(postId);
      setPosts((prev) =>
        prev.map((post) =>
          post.id === postId
            ? {
                ...post,
                upvotes: response.upvotes,
                userHasUpvoted: response.userHasUpvoted,
              }
            : post
        )
      );
    } catch {
      // Silently fail
    } finally {
      setUpvotingPosts((prev) => {
        const next = new Set(prev);
        next.delete(postId);
        return next;
      });
    }
  };

  // Handle create post
  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPostTitle.trim() || !newPostContent.trim()) return;

    setCreating(true);
    try {
      const tags = newPostTags
        .split(",")
        .map((t) => t.trim().toLowerCase())
        .filter((t) => t);

      await createPost({
        title: newPostTitle.trim(),
        content: newPostContent.trim(),
        tags,
      });

      // Reset form
      setNewPostTitle("");
      setNewPostContent("");
      setNewPostTags("");
      setShowCreateForm(false);

      // Reload posts
      setPage(1);
      loadPosts();
      loadTags();
    } catch (err) {
      setError("投稿の作成に失敗しました。");
    } finally {
      setCreating(false);
    }
  };

  // Clear filters
  const clearFilters = () => {
    setSearchQuery("");
    setSelectedTags([]);
    setSortOption("newest");
    setPage(1);
  };

  return (
    <div className="community-page">
      <h1 className="page-title">コミュニティ掲示板</h1>

      {/* Search & Filter Bar */}
      <div className="community-toolbar">
        <div className="search-row">
          <input
            type="text"
            className="search-input"
            placeholder="キーワードで検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <select
            className="sort-select"
            value={sortOption}
            onChange={(e) => handleSortChange(e.target.value as SortOption)}
          >
            <option value="newest">新着順</option>
            <option value="upvotes">人気順</option>
            <option value="views">閲覧数順</option>
            <option value="active">活発順</option>
          </select>
          <button
            className="btn-create"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? "✕ 閉じる" : "＋ 新規投稿"}
          </button>
        </div>

        {/* Tag Filter */}
        {availableTags.length > 0 && (
          <div className="tag-filter-row">
            <span className="tag-label">タグ:</span>
            <div className="tag-chips">
              {availableTags.map((tag) => (
                <button
                  key={tag.name}
                  className={`tag-chip ${
                    selectedTags.includes(tag.name) ? "active" : ""
                  }`}
                  onClick={() => handleTagClick(tag.name)}
                >
                  {tag.name}
                  <span className="tag-count">{tag.count}</span>
                </button>
              ))}
            </div>
            {(selectedTags.length > 0 || debouncedSearch) && (
              <button className="btn-clear-filters" onClick={clearFilters}>
                フィルターをクリア
              </button>
            )}
          </div>
        )}
      </div>

      {/* Inline Create Form */}
      {showCreateForm && (
        <form className="create-post-form" onSubmit={handleCreatePost}>
          <input
            type="text"
            className="input-title"
            placeholder="タイトル"
            value={newPostTitle}
            onChange={(e) => setNewPostTitle(e.target.value)}
            maxLength={200}
            required
          />
          <textarea
            className="input-content"
            placeholder="内容を入力してください..."
            value={newPostContent}
            onChange={(e) => setNewPostContent(e.target.value)}
            rows={5}
            required
          />
          <input
            type="text"
            className="input-tags"
            placeholder="タグ（カンマ区切り）: 例: 質問, コミュニケーション"
            value={newPostTags}
            onChange={(e) => setNewPostTags(e.target.value)}
          />
          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={() => setShowCreateForm(false)}
            >
              キャンセル
            </button>
            <button type="submit" className="btn-submit" disabled={creating}>
              {creating ? "投稿中..." : "投稿する"}
            </button>
          </div>
        </form>
      )}

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}

      {/* Results Info */}
      <div className="results-info">
        {total > 0 ? (
          <span>
            {total}件の投稿 (ページ {page}/{totalPages})
          </span>
        ) : loading ? (
          <span>読み込み中...</span>
        ) : (
          <span>投稿が見つかりません</span>
        )}
      </div>

      {/* Post List */}
      <div className="post-list">
        {loading && posts.length === 0 ? (
          <div className="loading-skeleton">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton-item" />
            ))}
          </div>
        ) : (
          posts.map((post) => (
            <article
              key={post.id}
              className={`post-item ${post.isPinned ? "pinned" : ""}`}
            >
             {/* Like Section */}
<div className="post-vote">
  <button
    className={`vote-btn ${post.userHasUpvoted ? "voted" : ""}`}
    onClick={() => handleUpvote(post.id)}
    disabled={upvotingPosts.has(post.id)}
    title={post.userHasUpvoted ? "いいねを取り消す" : "いいねする"}
  >
    <FiThumbsUp />
  </button>
  <span className="vote-count">{post.upvotes}</span>
</div>

              {/* Post Content */}
              <div className="post-content">
                <div className="post-header">
                  {post.isPinned && <span className="pinned-badge">📌</span>}
                  <h3 className="post-title">
                    <Link to={`/community/${post.id}`}>{post.title}</Link>
                  </h3>
                </div>

                {post.excerpt && (
                  <p className="post-excerpt">{post.excerpt}</p>
                )}

                <div className="post-meta">
                  <span className="post-author">
                    {post.author.fullName || post.author.username}
                  </span>
                  <span className="post-time">
                    {formatRelativeTime(post.createdAt)}
                  </span>
                  <span className="post-stats">
                    💬 {post.commentCount} · 👁 {post.views}
                  </span>
                  {post.tags.length > 0 && (
                    <div className="post-tags">
                      {post.tags.map((tag) => (
                        <button
                          key={tag}
                          className={`mini-tag ${
                            selectedTags.includes(tag) ? "active" : ""
                          }`}
                          onClick={() => handleTagClick(tag)}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            disabled={page === 1}
            onClick={() => setPage(1)}
          >
            «
          </button>
          <button
            className="page-btn"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ‹
          </button>

          {/* Page numbers */}
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum: number;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (page <= 3) {
              pageNum = i + 1;
            } else if (page >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = page - 2 + i;
            }
            return (
              <button
                key={pageNum}
                className={`page-btn ${page === pageNum ? "active" : ""}`}
                onClick={() => setPage(pageNum)}
              >
                {pageNum}
              </button>
            );
          })}

          <button
            className="page-btn"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            ›
          </button>
          <button
            className="page-btn"
            disabled={page === totalPages}
            onClick={() => setPage(totalPages)}
          >
            »
          </button>
        </div>
      )}
    </div>
  );
};

export default CommunityBoardPage;
