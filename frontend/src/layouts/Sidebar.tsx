import React from "react";

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar__service-name">インサイトブリッジ</div>

      <nav className="sidebar__nav">
        <ul className="nav-list">
          <li><a href="#">ホーム</a></li>
          <li><a href="#">会話シミュレーション</a></li>
          <li className="active"><a href="#">メッセージ感情分析</a></li>
          <li><a href="#">学生理解メモ</a></li>
          <li><a href="#">コミュニティ掲示板</a></li>
          <li><a href="#">設定</a></li>
          <li><a href="#">サインアウト</a></li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
