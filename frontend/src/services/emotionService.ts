const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface EmotionResult {
  emotion: string;
  confidence: string | number;
  sentiment: string;
  explanation: string;
  suggestions: string;
  timestamp: string;
}

export async function analyzeEmotion(message: string) {
  const response = await fetch(`${API_BASE}/emotion/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      student_name: "Student",
      teacher_name: "Teacher",
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail ?? "Emotion analysis failed");
  }

  return (await response.json()) as EmotionResult;
}