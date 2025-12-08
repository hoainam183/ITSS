from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime
import uuid

from app.models.education import ConversationScenario, ConversationSimulation, SimulationMessage
from app.schemas.conversation import (
    ScenarioResponse,
    ScenarioListResponse,
    StartSessionRequest,
    StartSessionResponse,
    ReplyRequest,
    ReplyResponse,
    EndSessionResponse,
    ScoreBreakdown,
    SessionFeedback,
    SessionHistoryResponse,
    MessageItem,
    CompletedSessionItem,
    CompletedSessionsResponse,
)
from app.services.conversation_ai import (
    generate_student_response,
    evaluate_teacher_response,
    generate_session_feedback,
)

router = APIRouter(prefix="/conversation", tags=["Conversation Simulation"])

# ============================================
# IN-MEMORY SESSION STORAGE
# (Option B: Only save to DB when session ends)
# ============================================

# Structure: { session_id: { scenario, messages, scores, started_at } }
active_sessions: Dict[str, dict] = {}


# ============================================
# SCENARIO ENDPOINTS
# ============================================

@router.get("/scenarios", response_model=ScenarioListResponse)
async def get_scenarios():
    """
    Get all available conversation scenarios
    """
    scenarios = await ConversationScenario.find_all().to_list()
    
    scenario_list = [
        ScenarioResponse(
            id=str(scenario.id),
            title=scenario.title,
            description=scenario.description or "",
            difficulty=scenario.difficulty,
            category=scenario.category,
            initialMessage=scenario.initial_message,
            goals=[],  # Can be added later
        )
        for scenario in scenarios
    ]
    
    return ScenarioListResponse(scenarios=scenario_list, total=len(scenario_list))


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    """
    Get a specific scenario by ID
    """
    from beanie import PydanticObjectId
    
    try:
        scenario = await ConversationScenario.get(PydanticObjectId(scenario_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return ScenarioResponse(
        id=str(scenario.id),
        title=scenario.title,
        description=scenario.description or "",
        difficulty=scenario.difficulty,
        category=scenario.category,
        initialMessage=scenario.initial_message,
        goals=[],
    )


# ============================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================

@router.post("/simulation/start", response_model=StartSessionResponse)
async def start_simulation(request: StartSessionRequest):
    """
    Start a new conversation simulation session
    """
    from beanie import PydanticObjectId
    
    # Get scenario
    try:
        scenario = await ConversationScenario.get(PydanticObjectId(request.scenario_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create session ID
    session_id = str(uuid.uuid4())
    
    # Store in memory (Option B: not saving to DB yet)
    active_sessions[session_id] = {
        "scenario_id": str(scenario.id),
        "scenario_title": scenario.title,
        "scenario": scenario,
        "messages": [
            {
                "role": "student",
                "content": scenario.initial_message,
                "timestamp": datetime.now(),
                "scores": None,
            }
        ],
        "all_scores": [],
        "started_at": datetime.now(),
    }
    
    return StartSessionResponse(
        sessionId=session_id,
        scenarioId=str(scenario.id),
        initialMessage=scenario.initial_message,
        scenarioTitle=scenario.title,
    )


@router.post("/simulation/{session_id}/reply", response_model=ReplyResponse)
async def send_reply(session_id: str, request: ReplyRequest):
    """
    Send teacher's reply and get AI evaluation + student response
    """
    # Check session exists
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = active_sessions[session_id]
    
    # 1. Evaluate teacher's response
    scores = await evaluate_teacher_response(
        scenario=session["scenario"],
        conversation_history=session["messages"],
        teacher_message=request.content,
    )
    
    # 2. Generate student response
    student_reply = await generate_student_response(
        scenario=session["scenario"],
        conversation_history=session["messages"],
        teacher_message=request.content,
    )
    
    # Add teacher message to history
    session["messages"].append({
        "role": "teacher",
        "content": request.content,
        "timestamp": datetime.now(),
        "scores": scores.model_dump(),
    })
    
    # Add student response to history
    session["messages"].append({
        "role": "student",
        "content": student_reply,
        "timestamp": datetime.now(),
        "scores": None,
    })
    
    # Track scores for session summary
    session["all_scores"].append(scores.model_dump())
    
    # Calculate turn number (teacher turns only)
    turn_number = len(session["all_scores"])
    
    return ReplyResponse(
        scores=scores,
        studentReply=student_reply,
        turnNumber=turn_number,
    )


@router.post("/simulation/{session_id}/end", response_model=EndSessionResponse)
async def end_simulation(session_id: str):
    """
    End the simulation session, get feedback, and save to database
    """
    # Check session exists
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = active_sessions[session_id]
    
    # Calculate average scores
    all_scores = session["all_scores"]
    if not all_scores:
        raise HTTPException(status_code=400, detail="No conversation turns to evaluate")
    
    avg_sincerity = sum(s["sincerity"] for s in all_scores) // len(all_scores)
    avg_appropriateness = sum(s["appropriateness"] for s in all_scores) // len(all_scores)
    avg_relevance = sum(s["relevance"] for s in all_scores) // len(all_scores)
    
    average_scores = ScoreBreakdown(
        sincerity=avg_sincerity,
        appropriateness=avg_appropriateness,
        relevance=avg_relevance,
    )
    
    # Calculate duration
    duration = int((datetime.now() - session["started_at"]).total_seconds())
    
    # Generate feedback using AI
    feedback = await generate_session_feedback(
        scenario=session["scenario"],
        conversation_history=session["messages"],
        all_scores=all_scores,
    )
    
    # Save to database (Option B)
    from beanie import PydanticObjectId
    
    # Convert messages to SimulationMessage format
    simulation_messages = []
    for msg in session["messages"]:
        sim_msg = SimulationMessage(
            sender=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"],
        )
        if msg["scores"]:
            sim_msg.sincerity_score = msg["scores"]["sincerity"]
            sim_msg.appropriateness_score = msg["scores"]["appropriateness"]
            sim_msg.relevance_score = msg["scores"]["relevance"]
        simulation_messages.append(sim_msg)
    
    # Create and save simulation record
    simulation = ConversationSimulation(
        user_id=PydanticObjectId("000000000000000000000000"),  # TODO: Get from auth
        scenario_id=PydanticObjectId(session["scenario_id"]),
        messages=simulation_messages,
        overall_score=(avg_sincerity + avg_appropriateness + avg_relevance) // 3,
        feedback=feedback.summary,
        started_at=session["started_at"],
        completed_at=datetime.now(),
        duration=duration,
    )
    await simulation.insert()
    
    # Remove from active sessions
    del active_sessions[session_id]
    
    return EndSessionResponse(
        averageScores=average_scores,
        totalTurns=len(all_scores),
        durationSeconds=duration,
        feedback=feedback,
    )


@router.get("/simulation/{session_id}", response_model=SessionHistoryResponse)
async def get_session(session_id: str):
    """
    Get current session state (for reconnection or debugging)
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = active_sessions[session_id]
    
    messages = [
        MessageItem(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"],
            scores=ScoreBreakdown(**msg["scores"]) if msg["scores"] else None,
        )
        for msg in session["messages"]
    ]
    
    return SessionHistoryResponse(
        sessionId=session_id,
        scenarioId=session["scenario_id"],
        scenarioTitle=session["scenario_title"],
        messages=messages,
        status="active",
        startedAt=session["started_at"],
        completedAt=None,
    )


# ============================================
# COMPLETED SESSIONS HISTORY ENDPOINTS
# ============================================

@router.get("/history", response_model=CompletedSessionsResponse)
async def get_completed_sessions(limit: int = 10, skip: int = 0):
    """
    Get list of completed simulation sessions (history)
    Optimized: Batch fetch scenarios to avoid N+1 query
    """
    # Query completed sessions, sorted by completed_at descending
    sessions = await ConversationSimulation.find(
        ConversationSimulation.completed_at != None
    ).sort(-ConversationSimulation.completed_at).skip(skip).limit(limit).to_list()
    
    if not sessions:
        return CompletedSessionsResponse(sessions=[], total=0)
    
    # Get total count
    total = await ConversationSimulation.find(
        ConversationSimulation.completed_at != None
    ).count()
    
    # OPTIMIZED: Batch fetch all scenarios at once (instead of N queries)
    scenario_ids = list(set(s.scenario_id for s in sessions))
    scenarios = await ConversationScenario.find(
        {"_id": {"$in": scenario_ids}}
    ).to_list()
    scenario_map = {str(s.id): s.title for s in scenarios}
    
    # Build response
    session_items = []
    for session in sessions:
        scenario_title = scenario_map.get(str(session.scenario_id), "Unknown Scenario")
        teacher_turns = len([m for m in session.messages if m.sender == "teacher"])
        
        session_items.append(CompletedSessionItem(
            sessionId=str(session.id),
            scenarioId=str(session.scenario_id),
            scenarioTitle=scenario_title,
            overallScore=session.overall_score or 0,
            totalTurns=teacher_turns,
            durationSeconds=session.duration,
            feedbackSummary=session.feedback or "",
            completedAt=session.completed_at,
        ))
    
    return CompletedSessionsResponse(sessions=session_items, total=total)


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
async def get_completed_session_detail(session_id: str):
    """
    Get details of a specific completed session
    """
    from beanie import PydanticObjectId
    
    try:
        session = await ConversationSimulation.get(PydanticObjectId(session_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get scenario title
    scenario = await ConversationScenario.get(session.scenario_id)
    scenario_title = scenario.title if scenario else "Unknown Scenario"
    
    # Convert messages
    messages = []
    for msg in session.messages:
        scores = None
        if msg.sender == "teacher" and msg.sincerity_score is not None:
            scores = ScoreBreakdown(
                sincerity=msg.sincerity_score,
                appropriateness=msg.appropriateness_score or 0,
                relevance=msg.relevance_score or 0,
            )
        messages.append(MessageItem(
            role=msg.sender,
            content=msg.content,
            timestamp=msg.timestamp,
            scores=scores,
        ))
    
    return SessionHistoryResponse(
        sessionId=str(session.id),
        scenarioId=str(session.scenario_id),
        scenarioTitle=scenario_title,
        messages=messages,
        status="completed",
        startedAt=session.started_at,
        completedAt=session.completed_at,
    )

