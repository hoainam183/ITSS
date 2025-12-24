import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./HomePage.css";

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const quickLinks = [
    {
      title: "メッセージ感情分析",
      description: "メッセージの感情とトーンを分析します",
      path: "/emotion-analysis",
      icon: "📊",
    },
    {
      title: "会話シミュレーション",
      description: "AIシナリオで会話を練習します",
      path: "/conversation-simulation",
      icon: "💬",
    },
    {
      title: "コミュニティ掲示板",
      description: "教員間の情報共有",
      path: "/community",
      icon: "👥",
    },
    {
      title: "プロフィール",
      description: "プロフィール情報の表示・編集",
      path: "/profile",
      icon: "👤",
    },
  ];

  return (
    <section className="home-page">
      <h1 className="welcome-header">
        ようこそ、{user?.username || "ユーザー"}さん
      </h1>
      
      <div className="quick-links-section">
        <h2 className="quick-links-title">主要機能へのアクセス</h2>
        <div className="quick-links-grid">
          {quickLinks.map((link) => (
            <div
              key={link.path}
              className="quick-link-card"
              onClick={() => navigate(link.path)}
            >
              <div className="quick-link-icon">{link.icon}</div>
              <h3 className="quick-link-title">{link.title}</h3>
              <p className="quick-link-description">{link.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HomePage;

