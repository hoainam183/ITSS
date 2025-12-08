import React from "react";
import Button from "../components/Button";
import ResultBox from "../components/ResultBox";

const CommunityBoardPage: React.FC = () => {
  return (
    <>
      {/* Title */}
      <h1 className="page-title">コミュニティ掲示板画面</h1>

      {/* Search + Create */}
      <div style={{ display: "flex", gap: 12, marginBottom: 25 }}>
        <input
          type="text"
          placeholder="トピックを検索..."
          className="analysis-textarea"
          style={{ height: 45 }}
        />

        <Button variant="primary" className="button-community">
          新規投稿を作成
        </Button>
      </div>

      {/* Topic List */}
      <ResultBox title="議論トピック一覧（情報共有と学び合い）">
        <div style={{ display: "flex", flexDirection: "column", gap: 15 }}>
          <div className="result-box" style={{ padding: 15 }}>
            [リスト] トピック：
            「文化的な反応をどう理解するか」 (10コメント)
          </div>

          <div className="result-box" style={{ padding: 15 }}>
            [リスト] トピック：
            「共感力を高めるためのトレーニング法」 (3コメント)
          </div>
        </div>
      </ResultBox>
    </>
  );
};

export default CommunityBoardPage;
