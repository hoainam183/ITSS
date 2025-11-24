import json
from datetime import datetime
from fastapi import HTTPException
from app.services.ai_client import get_ai_client, get_model

client = get_ai_client()


async def analyze_message(message: str, student_name: str, teacher_name: str):
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message must not be empty")

    system_prompt = (
        "You are an expert in educational sentiment analysis.\n"
        "Return ONLY valid JSON with fields: emotion, confidence, sentiment, "
        "explanation, suggestions. Reply in English."
    )
    user_prompt = (
        f"Student: {student_name}\nTeacher: {teacher_name}\n"
        f'Message: "{message}"\nReturn JSON analysis in English.'
    )

    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```"):
            parts = result_text.split("```")
            result_text = parts[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)
        data["timestamp"] = datetime.now().isoformat()
        return data
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI service error: {exc}") from exc
        