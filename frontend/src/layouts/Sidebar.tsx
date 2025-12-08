import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar: React.FC = () => {
  const navLinks = [
    { label: "ホーム", to: "/" },
    { label: "会話シミュレーション", to: "/conversation-simulation" },
    { label: "メッセージ感情分析", to: "/emotion-analysis" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">インサイトブリッジ</div>

      <nav className="sidebar-nav">
        <ul>
          {navLinks.map(({ label, to }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
          <li>
            <a className="nav-link" href="#">
              学生リスト
            </a>
          </li>
          <li>
            <a className="nav-link" href="#">
              コミュニティ掲示板
            </a>
          </li>
          <li>
            <a className="nav-link" href="#">
              設定
            </a>
          </li>
          <li className="nav-separator" />
          <li>
            <a className="nav-link signout" href="#">
              サインアウト
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;