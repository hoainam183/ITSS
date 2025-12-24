import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const Sidebar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">インサイトブリッジ</div>

      <nav className="sidebar-nav">
        <ul>
          <li className="nav-item">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              ホーム
            </NavLink>
          </li>

          {isAuthenticated && (
            <>
              <li className="nav-item">
                <NavLink
                  to="/conversation-simulation"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  会話シミュレーション
                </NavLink>
              </li>

              <li className="nav-item">
                <NavLink
                  to="/community"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  コミュニティ掲示板
                </NavLink>
              </li>

              <li className="nav-item">
                <NavLink
                  to="/emotion-analysis"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  メッセージ感情分析
                </NavLink>
              </li>
            </>
          )}

          <li className="nav-separator" />

          {isAuthenticated ? (
            <>
              {user && (
                <li className="nav-item user-info">
                  <div className="user-display">
                    {user.profile.avatar && (
                      <img 
                        src={user.profile.avatar} 
                        alt={user.username}
                        className="user-avatar"
                        onError={(e) => {
                          // Hide avatar if image fails to load
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    )}
                    <span className="user-name">{user.username}</span>
                  </div>
                </li>
              )}

              <li className="nav-item">
                <NavLink
                  to="/profile"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  設定
                </NavLink>
              </li>

              <li className="nav-item signout">
                <button
                  onClick={handleLogout}
                  className="nav-link logout-btn"
                >
                  <svg 
                    className="logout-icon" 
                    width="18" 
                    height="18" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  >
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  サインアウト
                </button>
              </li>
            </>
          ) : (
            <>
              <li className="nav-item">
                <NavLink
                  to="/login"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  ログイン
                </NavLink>
              </li>

              <li className="nav-item">
                <NavLink
                  to="/register"
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "active" : ""}`
                  }
                >
                  登録
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
