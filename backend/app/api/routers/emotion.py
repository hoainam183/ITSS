from fastapi import APIRouter
from app.schemas.emotion import EmotionRequest, EmotionResponse
from app.services.emotion_analysis import analyze_message

router = APIRouter(prefix="/emotion", tags=["Emotion"])

@router.post("/analyze", response_model=EmotionResponse)
async def analyze(request: EmotionRequest):
    result = await analyze_message(
        message=request.message,
        student_name=request.student_name or "Anonymous",
        teacher_name=request.teacher_name or "Teacher",
    )
    return result