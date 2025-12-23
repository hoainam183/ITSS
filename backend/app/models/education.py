from typing import List, Optional
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

# --- Collection 2: Conversation Scenarios ---
class ExpectedResponse(BaseModel):
    teacher_message: str = Field(..., alias="teacherMessage")
    student_reaction: str = Field(..., alias="studentReaction")
    points: int
    feedback: str

class ConversationScenario(Document):
    title: str
    description: Optional[str] = None
    difficulty: str # "easy", "medium", "hard"
    category: str   # "classroom", "parent", "academic"
    initial_message: str = Field(..., alias="initialMessage")
    expected_responses: List[ExpectedResponse] = Field(default=[], alias="expectedResponses")
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Settings:
        name = "conversation_scenarios"

# --- Collection 5: Conversation Simulations ---
class SimulationMessage(BaseModel):
    sender: str # "teacher" or "student"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    emotion: Optional[str] = None
    sincerity_score: Optional[int] = Field(None, alias="sincerityScore")
    appropriateness_score: Optional[int] = Field(None, alias="appropriatenessScore")
    relevance_score: Optional[int] = Field(None, alias="relevanceScore")

class ConversationSimulation(Document):
    user_id: PydanticObjectId = Field(..., alias="userId")
    scenario_id: PydanticObjectId = Field(..., alias="scenarioId")
    messages: List[SimulationMessage] = []
    overall_score: Optional[int] = Field(None, alias="overallScore")
    feedback: Optional[str] = None
    
    started_at: datetime = Field(default_factory=datetime.now, alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    duration: int = 0 # seconds

    class Settings:
        name = "conversation_simulations"

# --- Collection 6: Message Analyses ---
class AnalysisResult(BaseModel):
    primary_emotion: str = Field(..., alias="primaryEmotion")
    secondary_emotions: List[str] = Field([], alias="secondaryEmotions")
    tone: Optional[str] = None
    confidence: float = 0.0
    keywords: List[str] = []
    sentiment: str # "positive", "negative", "neutral"

class Suggestion(BaseModel):
    approach: str
    recommended_phrases: List[str] = Field([], alias="recommendedPhrases")
    things_to_avoid: List[str] = Field([], alias="thingsToAvoid")

class MessageAnalysis(Document):
    teacher_id: PydanticObjectId = Field(..., alias="teacherId")
    student_id: Optional[PydanticObjectId] = Field(None, alias="studentId")
    original_message: str = Field(..., alias="originalMessage")
    analysis_result: Optional[AnalysisResult] = Field(None, alias="analysisResult")
    suggestions: List[Suggestion] = []
    
    analyzed_at: datetime = Field(default_factory=datetime.now, alias="analyzedAt")

    class Settings:
        name = "message_analyses"