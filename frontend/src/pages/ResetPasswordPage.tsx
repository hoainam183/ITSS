import React, { useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { resetPassword, AuthApiError } from "../services/authApi";

const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useParams<{ token: string }>();
  
  const [formData, setFormData] = useState({
    newPassword: "",
    confirmPassword: "",
  });
  
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.newPassword || !formData.confirmPassword) {
      setError("すべてのフィールドを入力してください");
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError("パスワードが一致しません");
      return;
    }

    if (formData.newPassword.length < 6) {
      setError("パスワードは6文字以上である必要があります");
      return;
    }

    if (!token) {
      setError("無効なリセットトークンです");
      return;
    }

    setIsLoading(true);

    try {
      await resetPassword({
        token,
        newPassword: formData.newPassword,
      });
      
      alert("パスワードがリセットされました！ログインしてください。");
      navigate("/login");
    } catch (err) {
      if (err instanceof AuthApiError) {
        setError(err.message);
      } else {
        setError("パスワードのリセットに失敗しました。もう一度お試しください。");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-container">
        <h1 className="auth-title">新しいパスワード設定</h1>
        <p className="auth-description">
          新しいパスワードを入力してください。
        </p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="newPassword">新しいパスワード</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleChange}
              placeholder="新しいパスワードを入力（6文字以上）"
              disabled={isLoading}
              autoComplete="new-password"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">パスワード確認</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="パスワードを再入力"
              disabled={isLoading}
              autoComplete="new-password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? "リセット中..." : "パスワードをリセット"}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            <Link to="/login" className="auth-link">
              ログインページに戻る
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
};

export default ResetPasswordPage;
