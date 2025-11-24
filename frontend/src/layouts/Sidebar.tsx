import React from "react";

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">インサイトブリッジ</div>

      <nav className="sidebar-nav">
        <ul>
          <li className="nav-item">
            <a href="#">ホーム</a>
          </li>
          <li className="nav-item">
            <a href="#">会話シミュレーション</a>
          </li>
          {/* Mục đang chọn được đánh dấu active */}
          <li className="nav-item active">
            <a href="#">メッセージ感情分析</a>
          </li>
          <li className="nav-item">
            <a href="#">学生リスト</a>
          </li>
          <li className="nav-item">
            <a href="#">コミュニティ掲示板</a>
          </li>
          <li className="nav-item">
            <a href="#">設定</a>
          </li>
          <li className="nav-separator" />
          <li className="nav-item signout">
            <a href="#">サインアウト</a>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;