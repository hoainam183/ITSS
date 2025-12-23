import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { forgotPassword, resetPassword, AuthApiError } from "../services/authApi";

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<"email" | "reset">("email");
  const [email, setEmail] = useState("");
  
  // Reset form data
  const [resetData, setResetData] = useState({
    token: "",
    newPassword: "",
    confirmPassword: "",
  });
  
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!email) {
      setError("メールアドレスを入力してください");
      return;
    }

    setIsLoading(true);

    try {
      const response = await forgotPassword({ email });
      setSuccess(response.message);
      
      // Move to reset step after successful email submission
      setTimeout(() => {
        setStep("reset");
        setSuccess("");
      }, 2000);
    } catch (err) {
      if (err instanceof AuthApiError) {
        setError(err.message);
      } else {
        setError("リクエストの送信に失敗しました。もう一度お試しください。");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResetData({
      ...resetData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Validation
    if (!resetData.token || !resetData.newPassword || !resetData.confirmPassword) {
      setError("すべてのフィールドを入力してください");
      return;
    }

    if (resetData.newPassword !== resetData.confirmPassword) {
      setError("パスワードが一致しません");
      return;
    }

    if (resetData.newPassword.length < 6) {
      setError("パスワードは6文字以上である必要があります");
      return;
    }

    setIsLoading(true);

    try {
      await resetPassword({
        token: resetData.token,
        newPassword: resetData.newPassword,
      });
      
      setSuccess("パスワードがリセットされました！");
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate("/login");
      }, 2000);
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
        {step === "email" ? (
          <>
            <h1 className="auth-title">パスワードリセット</h1>
            <p className="auth-description">
              登録済みのメールアドレスを入力してください。パスワードリセット用のトークンをお送りします。
            </p>
            
            <form onSubmit={handleEmailSubmit} className="auth-form">
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

              <div className="form-group">
                <label htmlFor="email">メールアドレス</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="メールアドレスを入力"
                  disabled={isLoading}
                  autoComplete="email"
                  required
                />
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={isLoading}
              >
                {isLoading ? "送信中..." : "リセットトークンを送信"}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                <Link to="/login" className="auth-link">
                  ログインページに戻る
                </Link>
              </p>
            </div>
          </>
        ) : (
          <>
            <h1 className="auth-title">新しいパスワード設定</h1>
            <p className="auth-description">
              メールで受け取ったトークンと新しいパスワードを入力してください。
            </p>
            
            <form onSubmit={handleResetSubmit} className="auth-form">
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

              <div className="form-group">
                <label htmlFor="token">リセットトークン</label>
                <input
                  type="text"
                  id="token"
                  name="token"
                  value={resetData.token}
                  onChange={handleResetChange}
                  placeholder="メールで受け取ったトークンを入力"
                  disabled={isLoading}
                  required
                />
                <small style={{ color: "#666", fontSize: "0.85rem" }}>
                  ※ メール（{email}）に送信されたトークンを入力してください
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="newPassword">新しいパスワード</label>
                <input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={resetData.newPassword}
                  onChange={handleResetChange}
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
                  value={resetData.confirmPassword}
                  onChange={handleResetChange}
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
                <button
                  onClick={() => setStep("email")}
                  className="text-button"
                  disabled={isLoading}
                >
                  メールアドレスを変更
                </button>
                {" | "}
                <Link to="/login" className="auth-link">
                  ログインページに戻る
                </Link>
              </p>
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default ForgotPasswordPage;
