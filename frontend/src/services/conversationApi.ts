/**
 * Conversation Simulation API Service
 * Connects to backend /conversation endpoints
 */

import { getAuthHeaders } from "./authApi";

const API_BASE = "http://localhost:8000/conversation";

// ============================================
// TYPES
// ============================================

export interface Scenario {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  category: string;
  initialMessage: string;
  goals: string[];
}

export interface ScoreBreakdown {
  sincerity: number;      // 本音度
  appropriateness: number; // 適切さ
  relevance: number;       // 関連性
}

export interface StartSessionResponse {
  sessionId: string;
  scenarioId: string;
  initialMessage: string;
  scenarioTitle: string;
}

export interface ReplyResponse {
  scores: ScoreBreakdown;
  studentReply: string;
  turnNumber: number;
}

export interface SessionFeedback {
  summary: string;
  strengths: string[];
  improvements: string[];
  suggestions: string[];
}

export interface EndSessionResponse {
  averageScores: ScoreBreakdown;
  totalTurns: number;
  durationSeconds: number;
  feedback: SessionFeedback;
}

// ============================================
// API ERROR CLASS
// ============================================

export class ApiError extends Error {
  public status: number;
  public retryable: boolean;

  constructor(message: string, status: number, retryable: boolean = false) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryable = retryable;
  }
}


// ============================================
// API FUNCTIONS
// ============================================

/**
 * Fetch all available scenarios
 */
export async function fetchScenarios(): Promise<Scenario[]> {
  try {
    const response = await fetch(`${API_BASE}/scenarios`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new ApiError(
        "シナリオの取得に失敗しました",
        response.status,
        true
      );
    }
    
    const data = await response.json();
    return data.scenarios;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Start a new simulation session
 */
export async function startSession(scenarioId: string): Promise<StartSessionResponse> {
  try {
    const response = await fetch(`${API_BASE}/simulation/start`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ scenarioId }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || "セッションの開始に失敗しました",
        response.status,
        true
      );
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Send teacher's reply and get AI response
 */
export async function sendReply(
  sessionId: string,
  content: string
): Promise<ReplyResponse> {
  try {
    const response = await fetch(`${API_BASE}/simulation/${sessionId}/reply`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ content }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || "メッセージの送信に失敗しました",
        response.status,
        true // Retryable for message sending
      );
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * End session and get feedback
 */
export async function endSession(sessionId: string): Promise<EndSessionResponse> {
  try {
    const response = await fetch(`${API_BASE}/simulation/${sessionId}/end`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || "セッションの終了に失敗しました",
        response.status,
        false
      );
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

// ============================================
// SESSION HISTORY
// ============================================

export interface CompletedSession {
  sessionId: string;
  scenarioId: string;
  scenarioTitle: string;
  overallScore: number;
  totalTurns: number;
  durationSeconds: number;
  feedbackSummary: string;
  completedAt: string;
}

export interface CompletedSessionsResponse {
  sessions: CompletedSession[];
  total: number;
}

export interface SessionDetail {
  sessionId: string;
  scenarioId: string;
  scenarioTitle: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
    scores?: ScoreBreakdown;
  }>;
  status: string;
  startedAt: string;
  completedAt: string | null;
}

/**
 * Fetch completed sessions history
 */
export async function fetchSessionHistory(
  limit: number = 10,
  skip: number = 0
): Promise<CompletedSessionsResponse> {
  try {
    const response = await fetch(
      `${API_BASE}/history?limit=${limit}&skip=${skip}`,
      {
        headers: getAuthHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new ApiError("履歴の取得に失敗しました", response.status, true);
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

/**
 * Fetch details of a specific completed session
 */
export async function fetchSessionDetail(
  sessionId: string
): Promise<SessionDetail> {
  try {
    const response = await fetch(`${API_BASE}/history/${sessionId}`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new ApiError("セッション詳細の取得に失敗しました", response.status, false);
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("ネットワークエラーが発生しました", 0, true);
  }
}

