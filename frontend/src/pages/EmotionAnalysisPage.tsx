import React, { useState } from "react";
import MainLayout from "../layouts/MainLayout";
import Button from "../components/Button";
import ResultBox from "../components/ResultBox";

// Định nghĩa Interface cho Kết quả Phân tích Cảm xúc
interface EmotionAnalysisResult {
  emotion: string;
  percentage: string;
  suggestion: string;
  sampleText: string;
}

const EmotionAnalysisPage: React.FC = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState<EmotionAnalysisResult | null>(null); 

  // Dữ liệu mô phỏng kết quả
  const sampleResult: EmotionAnalysisResult = {
    emotion: "不安 (Lo lắng)",
    percentage: "55%",
    suggestion: "不安な感情を認め、安心感を与える返信例：",
    sampleText: "先生はあなたの気持ちを尊重します。最近どう感じていますか？ここは安心して気持ちを話せる場所ですよ。",
  };

  const handleAnalyze = () => {
    // Logic gọi API sẽ ở đây
    setResult(sampleResult);
  };

  return (
    <MainLayout>
      <h1 className="page-title">メッセージ感情分析画面</h1>

      {/* Khu vực Nhập liệu */}
      <section className="input-section">
        <h2>分析対象の入力</h2>

        <textarea
          className="analysis-textarea"
          placeholder="学生から受け取ったメッセージやコメントを貼り付け"
          rows={6}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <div className="button-row">
          <Button variant="secondary">アップロード用画面へ</Button>
          <Button variant="primary" onClick={handleAnalyze} disabled={!text.trim()}>
            感情を分析
          </Button>
        </div>
      </section>

      {/* Khu vực Kết quả (Chỉ hiển thị khi có kết quả) */}
      {result && (
        <section className="result-section">
          <h2>分析結果（感情とトーンの可視化）</h2>

          <div className="result-grid">
            
            <ResultBox title="感情判定" className="emotion-box">
              <div className="emotion-display">
                <span className="main-emotion">{result.emotion}</span>
                <span className="percentage-tag">{result.percentage}</span>
              </div>
              <p className="analysis-detail">
                詳細な感情分析グラフやトーン評価がここに視覚化されます。
              </p>
            </ResultBox>

            <ResultBox title="教師への対応提案" className="suggestion-box">
              <p className="suggestion-preamble">{result.suggestion}</p>
              <div className="suggestion-text-area">
                {result.sampleText}
              </div>
            </ResultBox>

          </div>
        </section>
      )}
    </MainLayout>
  );
};

export default EmotionAnalysisPage;