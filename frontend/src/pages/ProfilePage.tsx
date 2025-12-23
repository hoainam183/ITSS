import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { updateProfile, AuthApiError } from "../services/authApi";

const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  
  const [formData, setFormData] = useState({
    fullName: "",
    school: "",
    experience: "",
    avatar: "",
  });
  
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Load user data when component mounts or user changes
  useEffect(() => {
    if (user) {
      setFormData({
        fullName: user.profile.fullName || "",
        school: user.profile.school || "",
        experience: user.profile.experience || "",
        avatar: user.profile.avatar || "",
      });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await updateProfile(formData);
      await refreshUser(); // Refresh user data
      setSuccess("プロフィールが更新されました");
      setIsEditing(false);
    } catch (err) {
      if (err instanceof AuthApiError) {
        setError(err.message);
      } else {
        setError("プロフィールの更新に失敗しました。もう一度お試しください。");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form to current user data
    if (user) {
      setFormData({
        fullName: user.profile.fullName || "",
        school: user.profile.school || "",
        experience: user.profile.experience || "",
        avatar: user.profile.avatar || "",
      });
    }
    setIsEditing(false);
    setError("");
    setSuccess("");
  };

  if (!user) {
    return (
      <section>
        <h1 className="page-title">プロフィール</h1>
        <p>ユーザー情報を読み込んでいます...</p>
      </section>
    );
  }

  return (
    <section className="profile-page">
      <h1 className="page-title">プロフィール</h1>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
      
      {success && (
        <div className="success-message" role="alert">
          {success}
        </div>
      )}

      <div className="profile-container">
        {/* Basic Info (Read-only) */}
        <div className="profile-section">
          <h2>基本情報</h2>
          <div className="profile-field">
            <label>ユーザー名</label>
            <p>{user.username}</p>
          </div>
          <div className="profile-field">
            <label>メールアドレス</label>
            <p>{user.email}</p>
          </div>
          <div className="profile-field">
            <label>登録日</label>
            <p>{new Date(user.createdAt).toLocaleDateString("ja-JP")}</p>
          </div>
        </div>

        {/* Editable Profile */}
        <div className="profile-section">
          <div className="section-header">
            <h2>詳細情報</h2>
            {!isEditing && (
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setIsEditing(true)}
              >
                編集
              </button>
            )}
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="fullName">氏名</label>
              {isEditing ? (
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  placeholder="氏名を入力"
                  disabled={isLoading}
                />
              ) : (
                <p className="profile-value">{user.profile.fullName || "未設定"}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="school">学校</label>
              {isEditing ? (
                <input
                  type="text"
                  id="school"
                  name="school"
                  value={formData.school}
                  onChange={handleChange}
                  placeholder="学校名を入力"
                  disabled={isLoading}
                />
              ) : (
                <p className="profile-value">{user.profile.school || "未設定"}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="experience">経験・専門分野</label>
              {isEditing ? (
                <textarea
                  id="experience"
                  name="experience"
                  value={formData.experience}
                  onChange={handleChange}
                  placeholder="経験や専門分野を入力"
                  disabled={isLoading}
                  rows={4}
                />
              ) : (
                <p className="profile-value">{user.profile.experience || "未設定"}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="avatar">アバターURL</label>
              {isEditing ? (
                <input
                  type="url"
                  id="avatar"
                  name="avatar"
                  value={formData.avatar}
                  onChange={handleChange}
                  placeholder="アバター画像のURLを入力"
                  disabled={isLoading}
                />
              ) : (
                <p className="profile-value">{user.profile.avatar || "未設定"}</p>
              )}
            </div>

            {isEditing && (
              <div className="form-actions">
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? "保存中..." : "保存"}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCancel}
                  disabled={isLoading}
                >
                  キャンセル
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </section>
  );
};

export default ProfilePage;
