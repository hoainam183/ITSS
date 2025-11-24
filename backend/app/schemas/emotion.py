from pydantic import BaseModel, Field
from typing import Optional, Union

class EmotionRequest(BaseModel):
    message: str = Field(..., min_length=1)
    student_name: Optional[str] = Field("Anonymous", alias="student_name")
    teacher_name: Optional[str] = Field("Teacher", alias="teacher_name")

    class Config:
        populate_by_name = True

class EmotionResponse(BaseModel):
    emotion: str
    confidence: Union[str, float]
    sentiment: str
    explanation: str
    suggestions: Union[str, list[str]]
    timestamp: str