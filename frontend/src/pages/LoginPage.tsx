import React, { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { AuthApiError } from "../services/authApi";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  // Get redirect path from location state, default to "/"
  const from = (location.state as any)?.from?.pathname || "/";

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(""); // Clear error on input change
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.email || !formData.password) {
      setError("すべてのフィールドを入力してください");
      return;
    }

    setIsLoading(true);

    try {
      await login({
        email: formData.email,
        password: formData.password,
      });
      
      // Redirect to original destination or home
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof AuthApiError) {
        setError(err.message);
      } else {
        setError("ログインに失敗しました。もう一度お試しください。");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-container">
        <h1 className="auth-title">ログイン</h1>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="メールアドレスを入力"
              disabled={isLoading}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="パスワードを入力"
              disabled={isLoading}
              autoComplete="current-password"
              required
            />
          </div>

          <div className="form-footer">
            <Link to="/forgot-password" className="forgot-password-link">
              パスワードをお忘れですか？
            </Link>
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? "ログイン中..." : "ログイン"}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            アカウントをお持ちでないですか？{" "}
            <Link to="/register" className="auth-link">
              新規登録
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
};

export default LoginPage;
