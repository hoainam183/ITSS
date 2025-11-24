import React, { useState } from "react";
import MainLayout from "../layouts/MainLayout";
import Button from "../components/Button";
import ResultBox from "../components/ResultBox";
import {
  analyzeEmotion,
  type EmotionResult,
} from "../services/emotionService";

const EmotionAnalysisPage: React.FC = () => {
  const [text, setText] = useState("");
  const [result, setResult] = useState<EmotionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeEmotion(text);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <h1 className="page-title">メッセージ感情分析画面</h1>

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
          <Button
            variant="primary"
            onClick={handleAnalyze}
            disabled={!text.trim() || loading}
          >
            {loading ? "分析中..." : "感情を分析"}
          </Button>
        </div>
      </section>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <section className="result-section">
          <ResultBox title="感情判定" className="emotion-box">
            <div className="emotion-display">
              <span className="main-emotion">{result.emotion}</span>
              <span className="percentage-tag">
                {typeof result.confidence === "number"
                  ? `${(result.confidence * 100).toFixed(0)}%`
                  : result.confidence}
              </span>
            </div>
            <p className="analysis-detail">{result.explanation}</p>
            <p className="analysis-detail">Sentiment: {result.sentiment}</p>
          </ResultBox>

          <ResultBox title="教師への対応提案" className="suggestion-box">
            {Array.isArray(result.suggestions) ? (
              <ul className="suggestion-list">
                {result.suggestions.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="suggestion-preamble">{result.suggestions}</p>
            )}
            <small>
              {new Date(result.timestamp).toLocaleString("ja-JP")}
            </small>
          </ResultBox>
        </section>
      )}
    </MainLayout>
  );
};

export default EmotionAnalysisPage;