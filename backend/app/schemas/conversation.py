from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================
# SCENARIO SCHEMAS
# ============================================

class ScenarioResponse(BaseModel):
    """Response schema for a single scenario"""
    id: str
    title: str
    description: str
    difficulty: str  # "easy", "medium", "hard"
    category: str    # "classroom", "academic", "personal"
    initial_message: str = Field(alias="initialMessage")
    goals: List[str] = []

    class Config:
        populate_by_name = True


class ScenarioListResponse(BaseModel):
    """Response schema for list of scenarios"""
    scenarios: List[ScenarioResponse]
    total: int


# ============================================
# SESSION SCHEMAS
# ============================================

class StartSessionRequest(BaseModel):
    """Request to start a new simulation session"""
    scenario_id: str = Field(alias="scenarioId")

    class Config:
        populate_by_name = True


class StartSessionResponse(BaseModel):
    """Response when starting a new session"""
    session_id: str = Field(alias="sessionId")
    scenario_id: str = Field(alias="scenarioId")
    initial_message: str = Field(alias="initialMessage")
    scenario_title: str = Field(alias="scenarioTitle")

    class Config:
        populate_by_name = True


# ============================================
# CONVERSATION SCHEMAS
# ============================================

class ScoreBreakdown(BaseModel):
    """Scores for evaluating teacher's response"""
    sincerity: int = Field(ge=0, le=100, description="本音度 - Độ chân thành")
    appropriateness: int = Field(ge=0, le=100, description="適切さ - Độ phù hợp")
    relevance: int = Field(ge=0, le=100, description="関連性 - Độ liên quan")


class ReplyRequest(BaseModel):
    """Request to send teacher's reply"""
    content: str = Field(min_length=1, description="Teacher's message content")


class ReplyResponse(BaseModel):
    """Response after teacher sends a reply"""
    scores: ScoreBreakdown
    student_reply: str = Field(alias="studentReply")
    turn_number: int = Field(alias="turnNumber")

    class Config:
        populate_by_name = True


# ============================================
# END SESSION SCHEMAS
# ============================================

class SessionFeedback(BaseModel):
    """Detailed feedback at the end of session"""
    summary: str = Field(description="Tóm tắt tổng quan")
    strengths: List[str] = Field(description="Điểm mạnh")
    improvements: List[str] = Field(description="Điểm cần cải thiện")
    suggestions: List[str] = Field(description="Gợi ý cho lần sau")


class EndSessionResponse(BaseModel):
    """Response when ending a session"""
    average_scores: ScoreBreakdown = Field(alias="averageScores")
    total_turns: int = Field(alias="totalTurns")
    duration_seconds: int = Field(alias="durationSeconds")
    feedback: SessionFeedback

    class Config:
        populate_by_name = True


# ============================================
# MESSAGE SCHEMAS (for history)
# ============================================

class MessageItem(BaseModel):
    """A single message in conversation history"""
    role: str  # "teacher" or "student"
    content: str
    timestamp: datetime
    scores: Optional[ScoreBreakdown] = None  # Only for teacher messages


class SessionHistoryResponse(BaseModel):
    """Full session history"""
    session_id: str = Field(alias="sessionId")
    scenario_id: str = Field(alias="scenarioId")
    scenario_title: str = Field(alias="scenarioTitle")
    messages: List[MessageItem]
    status: str  # "active" or "completed"
    started_at: datetime = Field(alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    class Config:
        populate_by_name = True


# ============================================
# COMPLETED SESSIONS LIST (for history view)
# ============================================

class CompletedSessionItem(BaseModel):
    """Summary of a completed session for list view"""
    session_id: str = Field(alias="sessionId")
    scenario_id: str = Field(alias="scenarioId")
    scenario_title: str = Field(alias="scenarioTitle")
    overall_score: int = Field(alias="overallScore")
    total_turns: int = Field(alias="totalTurns")
    duration_seconds: int = Field(alias="durationSeconds")
    feedback_summary: str = Field(alias="feedbackSummary")
    completed_at: datetime = Field(alias="completedAt")

    class Config:
        populate_by_name = True


class CompletedSessionsResponse(BaseModel):
    """List of completed sessions"""
    sessions: List[CompletedSessionItem]
    total: int

