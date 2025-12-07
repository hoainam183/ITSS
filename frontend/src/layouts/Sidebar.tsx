import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">インサイトブリッジ</div>

      <nav className="sidebar-nav">
        <ul>
          <li className="nav-item">
            <NavLink to="/">ホーム</NavLink>
          </li>

          <li className="nav-item">
            <NavLink to="/simulation">会話シミュレーション</NavLink>
          </li>

          <li className="nav-item">
            <NavLink
              to="/message-analysis"
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              メッセージ感情分析
            </NavLink>
          </li>

          <li className="nav-item">
            <NavLink to="/students">学生リスト</NavLink>
          </li>

          <li className="nav-item">
            <NavLink
              to="/community"
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              コミュニティ掲示板
            </NavLink>
          </li>

          <li className="nav-item">
            <NavLink to="/setting">設定</NavLink>
          </li>

          <li className="nav-separator" />

          <li className="nav-item signout">
            <NavLink to="/logout">サインアウト</NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
