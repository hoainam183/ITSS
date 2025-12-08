import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC = () => {
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
              to="/emotion-analysis"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              メッセージ感情分析
            </NavLink>
          </li>

          <li className="nav-item">
            <NavLink
              to="/students"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              学生リスト
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
              to="/setting"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              設定
            </NavLink>
          </li>

          <li className="nav-separator" />

          <li className="nav-item signout">
            <NavLink
              to="/logout"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              サインアウト
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
