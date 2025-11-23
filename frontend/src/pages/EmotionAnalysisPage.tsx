import React, { useState } from "react";
import MainLayout from "../layouts/MainLayout";

const EmotionAnalysisPage: React.FC = () => {
  const [text, setText] = useState("");

  return (
    <MainLayout>
      <h1 className="page-title">メッセージ感情分析画面</h1>

      <section className="section">
        <h2>分析対象の入力</h2>

        <textarea
          className="analysis-textarea"
          placeholder="【テキストエリア】学生から受け取ったメッセージやコメントを貼り付け"
          rows={6}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <div className="button-row">
          <button className="button-secondary">アップロード用画面へ</button>
          <button className="button-primary">感情を分析</button>
        </div>
      </section>

      <section className="section">
        <h2>分析結果（感情とトーンの可視化）</h2>

        <div className="result-grid">
          <div className="result-box">
            <h3>“感情判定”</h3>
            <p>主な感情例：不安 65% など</p>
            <div>ここに分析結果が入ります。</div>
          </div>

          <div className="result-box">
            <h3>“教師への対応提案”</h3>
            <p>不安を軽減し、安心感を与える返答例：</p>
            <div>
              ここに教師が返信する際の文例やヒントを表示。
              例：「最近どう感じていますか？ここは安心して気持ちを話せる場所ですよ。」
            </div>
          </div>
        </div>
      </section>
    </MainLayout>
  );
};

export default EmotionAnalysisPage;
