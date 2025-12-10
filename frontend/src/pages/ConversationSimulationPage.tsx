import React, { useEffect, useMemo, useRef, useState, useCallback } from "react";
import Button from "../components/Button";
import {
  fetchScenarios,
  startSession,
  sendReply,
  endSession,
  fetchSessionHistory,
  fetchSessionDetail,
  type Scenario,
  type ScoreBreakdown,
  type SessionFeedback,
  type ApiError,
  type CompletedSession,
  type SessionDetail,
} from "../services/conversationApi";

type Role = "student" | "teacher";

interface ConversationTurn {
  id: string;
  role: Role;
  content: string;
  timestamp: string;
  scores?: ScoreBreakdown;
}

interface ErrorState {
  message: string;
  retryable: boolean;
  retryAction?: () => void;
}

const generateTurnId = () =>
  `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;

const ConversationSimulationPage: React.FC = () => {
  // State
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [message, setMessage] = useState("");
  
  // Loading states
  const [loadingScenarios, setLoadingScenarios] = useState(false);
  const [startingSession, setStartingSession] = useState(false);
  const [sending, setSending] = useState(false);
  const [endingSession, setEndingSession] = useState(false);
  
  // Error state
  const [error, setError] = useState<ErrorState | null>(null);
  
  // Session tracking
  const [sessionScores, setSessionScores] = useState<ScoreBreakdown[]>([]);
  const [sessionFeedback, setSessionFeedback] = useState<{
    averageScores: ScoreBreakdown;
    totalTurns: number;
    durationSeconds: number;
    feedback: SessionFeedback;
  } | null>(null);
  
  // Session History
  const [historyList, setHistoryList] = useState<CompletedSession[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedHistorySession, setSelectedHistorySession] = useState<SessionDetail | null>(null);
  const [loadingHistoryDetail, setLoadingHistoryDetail] = useState(false);
  
  const chatHistoryRef = useRef<HTMLDivElement | null>(null);

  // Load scenarios and history on mount
  useEffect(() => {
    loadScenarios();
    loadHistory();
  }, []);

  // Reload history when session ends
  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const data = await fetchSessionHistory(5); // Last 5 sessions
      setHistoryList(data.sessions);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  // Load specific session detail
  const loadHistoryDetail = async (historySessionId: string) => {
    setLoadingHistoryDetail(true);
    try {
      const detail = await fetchSessionDetail(historySessionId);
      setSelectedHistorySession(detail);
    } catch (err) {
      console.error("Failed to load session detail:", err);
    } finally {
      setLoadingHistoryDetail(false);
    }
  };

  const loadScenarios = async () => {
    setLoadingScenarios(true);
    setError(null);
    try {
      const data = await fetchScenarios();
      setScenarios(data);
    } catch (err) {
      const apiError = err as ApiError;
      setError({
        message: apiError.message || "シナリオの取得に失敗しました",
        retryable: true,
        retryAction: loadScenarios,
      });
    } finally {
      setLoadingScenarios(false);
    }
  };

  const selectedScenario = useMemo(
    () => scenarios.find((s) => s.id === selectedScenarioId),
    [selectedScenarioId, scenarios]
  );

  // Handle scenario selection - starts a new session
  const handleSelectScenario = async (scenarioId: string) => {
    setError(null);
    setSelectedScenarioId(scenarioId);
    setTurns([]);
    setMessage("");
    setSessionScores([]);
    setSessionFeedback(null);
    setSessionId(null);

    if (!scenarioId) return;

    setStartingSession(true);
    try {
      const response = await startSession(scenarioId);
      setSessionId(response.sessionId);
      
      // Add initial student message
      setTurns([
        {
          id: generateTurnId(),
          role: "student",
          content: response.initialMessage,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      const apiError = err as ApiError;
      setError({
        message: apiError.message || "セッションの開始に失敗しました",
        retryable: true,
        retryAction: () => handleSelectScenario(scenarioId),
      });
      setSelectedScenarioId("");
    } finally {
      setStartingSession(false);
    }
  };

  // Handle sending message
  const handleSendMessage = async (retryContent?: string) => {
    const content = retryContent || message.trim();
    if (!content || !sessionId) return;
    
    setError(null);

    const userTurnId = generateTurnId();
    const userTurn: ConversationTurn = {
      id: userTurnId,
      role: "teacher",
      content,
      timestamp: new Date().toISOString(),
    };
    
    // Only add user turn if not retrying (already added)
    if (!retryContent) {
    setTurns((prev) => [...prev, userTurn]);
    setMessage("");
    }
    
    setSending(true);

    try {
      const response = await sendReply(sessionId, content);

      // Update teacher turn with scores
      setTurns((prev) => {
        const updated = prev.map((turn) =>
          turn.id === userTurnId || (retryContent && turn.role === "teacher" && !turn.scores)
            ? { ...turn, scores: response.scores }
            : turn
        );
        
        // Add student response
        return [
          ...updated,
          {
        id: generateTurnId(),
            role: "student" as Role,
            content: response.studentReply,
        timestamp: new Date().toISOString(),
          },
        ];
      });
      
      setSessionScores((prev) => [...prev, response.scores]);
    } catch (err) {
      const apiError = err as ApiError;
      setError({
        message: apiError.message || "メッセージの送信に失敗しました",
        retryable: true,
        retryAction: () => handleSendMessage(content),
      });
    } finally {
      setSending(false);
    }
  };

  // Handle ending session
  const handleEndSession = async () => {
    if (!sessionId || !sessionScores.length) return;
    
    setError(null);
    setEndingSession(true);

    try {
      const response = await endSession(sessionId);
      setSessionFeedback(response);
      setSessionId(null); // Session is now closed
      // Reload history to include the just-completed session
      loadHistory();
    } catch (err) {
      const apiError = err as ApiError;
      setError({
        message: apiError.message || "セッションの終了に失敗しました",
        retryable: true,
        retryAction: handleEndSession,
      });
    } finally {
      setEndingSession(false);
    }
  };

  // Auto-scroll chat
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [turns, sending]);

  const showEmptyState = !selectedScenarioId || turns.length === 0;
  const isSessionActive = sessionId !== null && !sessionFeedback;

  return (
    <section>
      <h1 className="page-title">会話シミュレーション</h1>

      <div className="simulation-wrapper">
        <div className="simulation-grid">
          {/* Left Column - Controls */}
          <div className="control-column">
            {/* Scenario Selection */}
            <section className="topic-card">
              <div className="topic-select-wrapper">
                <label htmlFor="topicSelect">シナリオを選択</label>
                <select
                  id="topicSelect"
                  className="topic-select"
                  value={selectedScenarioId}
                  onChange={(e) => handleSelectScenario(e.target.value)}
                  disabled={loadingScenarios || startingSession || isSessionActive}
                >
                  <option value="">シナリオを選択してください --</option>
                  {scenarios.map((scenario) => (
                    <option key={scenario.id} value={scenario.id}>
                      {scenario.title}
                    </option>
                  ))}
                </select>
                {startingSession && (
                  <span className="loading-text">セッション開始中...</span>
                )}
              </div>

              <div className="topic-details">
                {selectedScenario ? (
                  <>
                    <p className="topic-description">
                      {selectedScenario.description}
                    </p>
                    <div className="topic-meta">
                      <span className={`difficulty-badge ${selectedScenario.difficulty}`}>
                        {selectedScenario.difficulty === "easy" ? "初級" : 
                         selectedScenario.difficulty === "medium" ? "中級" : "上級"}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="topic-placeholder">
                    シナリオを選択すると説明が表示されます。
                  </p>
                )}
              </div>
            </section>

            {/* Session Summary / Feedback */}
            <section className="summary-card">
              <h3>セッション評価</h3>
              
              {sessionFeedback ? (
                <div className="feedback-content">
                  {/* Average Scores */}
                  <div className="score-tags summary">
                    <span className="score-chip">
                      本音度: {sessionFeedback.averageScores.sincerity}
                    </span>
                    <span className="score-chip">
                      適切さ: {sessionFeedback.averageScores.appropriateness}
                    </span>
                    <span className="score-chip">
                      関連性: {sessionFeedback.averageScores.relevance}
                    </span>
                  </div>
                  
                  {/* Session Stats */}
                  <p className="session-stats">
                    対話回数: {sessionFeedback.totalTurns}回 / 
                    所要時間: {Math.floor(sessionFeedback.durationSeconds / 60)}分
                    {sessionFeedback.durationSeconds % 60}秒
                  </p>
                  
                  {/* Feedback Summary */}
                  <div className="feedback-summary">
                    <p>{sessionFeedback.feedback.summary}</p>
                  </div>
                  
                  {/* Strengths */}
                  <div className="feedback-section">
                    <h4>✓ 良かった点</h4>
                    <ul>
                      {sessionFeedback.feedback.strengths.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Improvements */}
                  <div className="feedback-section">
                    <h4>△ 改善点</h4>
                    <ul>
                      {sessionFeedback.feedback.improvements.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Suggestions */}
                  <div className="feedback-section">
                    <h4>→ 次回へのアドバイス</h4>
                    <ul>
                      {sessionFeedback.feedback.suggestions.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* New Session Button */}
                  <Button
                    variant="primary"
                    onClick={() => {
                      setSelectedScenarioId("");
                      setSessionFeedback(null);
                      setTurns([]);
                      setSessionScores([]);
                    }}
                    className="new-session-btn"
                  >
                    新しいセッションを開始
                  </Button>
                </div>
              ) : isSessionActive ? (
                <div className="session-in-progress">
                  <div className="session-active-indicator">
                    <span className="session-pulse"></span>
                    <span className="session-active-text">セッション進行中</span>
                  </div>
                  {sessionScores.length > 0 && (
                    <>
                      <p className="turns-count">
                        現在の対話回数: {sessionScores.length}回
                      </p>
                      <div className="score-tags summary">
                        <span className="score-chip">
                          平均 本音度: {Math.round(sessionScores.reduce((a, s) => a + s.sincerity, 0) / sessionScores.length)}
                        </span>
                        <span className="score-chip">
                          平均 適切さ: {Math.round(sessionScores.reduce((a, s) => a + s.appropriateness, 0) / sessionScores.length)}
                        </span>
                        <span className="score-chip">
                          平均 関連性: {Math.round(sessionScores.reduce((a, s) => a + s.relevance, 0) / sessionScores.length)}
                        </span>
                      </div>
                    </>
                  )}
                  <p className="summary-placeholder">
                    「セッションを終了」を押すとフィードバックが表示されます。
                  </p>
                </div>
              ) : (
                <p className="summary-placeholder">
                  セッションを開始すると評価が表示されます。
                </p>
              )}
            </section>
          </div>

          {/* Right Column - Chat */}
          <div className="chat-column">
            <div className="chat-panel">
              <div className="chat-history" ref={chatHistoryRef}>
                {showEmptyState ? (
                  <div className="chat-empty">
                    <p>
                      会話を開始するには左側のリストからシナリオを選択してください。
                    </p>
                  </div>
                ) : (
                  <>
                    {turns.map((turn) => (
                    <div
                      key={turn.id}
                      className={`chat-bubble ${
                          turn.role === "student" ? "bubble-ai" : "bubble-teacher"
                      }`}
                    >
                      <span className="chat-meta">
                          {turn.role === "student" ? "学生" : "先生（あなた）"}・
                        {new Date(turn.timestamp).toLocaleTimeString("ja-JP", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                      <p>{turn.content}</p>
                      {turn.role === "teacher" && turn.scores && (
                        <div className="score-tags">
                          <span className="score-chip">
                              本音度: {turn.scores.sincerity}
                          </span>
                          <span className="score-chip">
                              適切さ: {turn.scores.appropriateness}
                          </span>
                          <span className="score-chip">
                              関連性: {turn.scores.relevance}
                          </span>
                        </div>
                      )}
                    </div>
                    ))}
                    
                    {/* Typing Indicator */}
                    {sending && (
                      <div className="chat-bubble bubble-ai typing-indicator">
                        <span className="chat-meta">学生</span>
                        <div className="typing-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Error Message with Retry */}
              {error && (
                <div className="error-container">
                  <p className="error-text">{error.message}</p>
                  {error.retryable && error.retryAction && (
                    <Button
                      variant="secondary"
                      onClick={error.retryAction}
                      className="retry-btn"
                    >
                      再試行
                    </Button>
                  )}
                </div>
              )}

              {/* Input Area */}
              <div className="chat-input">
                <textarea
                  className="chat-textarea"
                  placeholder={
                    isSessionActive
                      ? "返信を入力してください..."
                      : sessionFeedback
                      ? "セッションは終了しました"
                      : "シナリオを選択すると入力できます"
                  }
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={!isSessionActive || sending}
                  rows={3}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey && isSessionActive && message.trim()) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <div className="chat-actions">
                <Button
                  variant="secondary"
                    onClick={handleEndSession}
                    disabled={!isSessionActive || !sessionScores.length || endingSession}
                >
                    {endingSession ? "終了中..." : "セッションを終了"}
                </Button>
                <Button
                  variant="primary"
                    onClick={() => handleSendMessage()}
                    disabled={!message.trim() || !isSessionActive || sending}
                >
                  {sending ? "送信中..." : "送信"}
                </Button>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      {/* Session History Section */}
      <div className="history-section">
        <div className="history-header">
          <h3>セッション履歴</h3>
          <Button
            variant="secondary"
            onClick={loadHistory}
            disabled={loadingHistory}
            className="refresh-btn"
          >
            {loadingHistory ? "更新中..." : "更新"}
          </Button>
        </div>

        {historyList.length === 0 && !loadingHistory && (
          <p className="history-empty">まだ完了したセッションはありません</p>
        )}

        {loadingHistory && historyList.length === 0 && (
          <p className="history-loading">履歴を読み込み中...</p>
        )}

        <div className="history-list">
          {historyList.map((item) => (
            <div
              key={item.sessionId}
              className={`history-item ${
                selectedHistorySession?.sessionId === item.sessionId ? "active" : ""
              }`}
              onClick={() => loadHistoryDetail(item.sessionId)}
            >
              <div className="history-item-header">
                <span className="history-scenario">{item.scenarioTitle}</span>
                <span className="history-score">
                  スコア: {item.overallScore}点
                </span>
              </div>
              <div className="history-item-meta">
                <span>ターン: {item.totalTurns}</span>
                <span>時間: {Math.floor(item.durationSeconds / 60)}分{item.durationSeconds % 60}秒</span>
                <span className="history-date">
                  {new Date(item.completedAt).toLocaleDateString("ja-JP", {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              {item.feedbackSummary && (
                <p className="history-feedback-preview">
                  {item.feedbackSummary.length > 80
                    ? item.feedbackSummary.slice(0, 80) + "..."
                    : item.feedbackSummary}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Selected Session Detail Modal */}
        {selectedHistorySession && (
          <div className="history-detail-overlay" onClick={() => setSelectedHistorySession(null)}>
            <div className="history-detail-modal" onClick={(e) => e.stopPropagation()}>
              <div className="history-detail-header">
                <h4>{selectedHistorySession.scenarioTitle}</h4>
                <button
                  className="close-btn"
                  onClick={() => setSelectedHistorySession(null)}
                >
                  ✕
                </button>
              </div>
              
              {loadingHistoryDetail ? (
                <p className="history-loading">詳細を読み込み中...</p>
              ) : (
                <div className="history-detail-content">
                  <div className="history-detail-meta">
                    <span>
                      開始: {new Date(selectedHistorySession.startedAt).toLocaleString("ja-JP")}
                    </span>
                    {selectedHistorySession.completedAt && (
                      <span>
                        終了: {new Date(selectedHistorySession.completedAt).toLocaleString("ja-JP")}
                      </span>
                    )}
        </div>

                  <div className="history-messages">
                    {selectedHistorySession.messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`history-message ${msg.role === "teacher" ? "teacher" : "student"}`}
                      >
                        <div className="history-message-header">
                          <span className="history-message-role">
                            {msg.role === "teacher" ? "👨‍🏫 教師" : "👩‍🎓 学生"}
                          </span>
                          <span className="history-message-time">
                            {new Date(msg.timestamp).toLocaleTimeString("ja-JP", {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                        <p className="history-message-content">{msg.content}</p>
                        {msg.scores && (
                          <div className="history-message-scores">
                            <span>本音度: {msg.scores.sincerity}</span>
                            <span>適切さ: {msg.scores.appropriateness}</span>
                            <span>関連性: {msg.scores.relevance}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default ConversationSimulationPage;
