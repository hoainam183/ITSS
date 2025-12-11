"""
AI Service for Conversation Simulation
- Generate student responses (Vietnamese student characteristics)
- Evaluate teacher responses (3 independent scores)
- Generate session feedback
"""

import json
from typing import List, Dict, Any
from fastapi import HTTPException
from app.services.ai_client import get_ai_client, get_model
from app.schemas.conversation import ScoreBreakdown, SessionFeedback

# Initialize AI client
client = get_ai_client()


# ============================================
# HELPER: Parse JSON from AI response
# ============================================

def parse_json_response(response_text: str) -> dict:
    """Parse JSON from AI response, handling markdown code blocks"""
    text = response_text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    
    return json.loads(text)


# ============================================
# 1. GENERATE STUDENT RESPONSE
# ============================================

async def generate_student_response(
    scenario: Any,
    conversation_history: List[Dict],
    teacher_message: str,
) -> str:
    """
    AI đóng vai học sinh Việt Nam với đặc điểm:
    - Rụt rè, ngại nói
    - Sợ sai ngữ pháp
    - Dùng từ đơn giản
    - Đôi khi dùng tiếng Nhật không hoàn hảo
    - Thể hiện cảm xúc qua cách nói (nervous, grateful, confused)
    """
    
    # Build conversation context
    history_text = "\n".join([
        f"{'学生' if msg['role'] == 'student' else '先生'}: {msg['content']}"
        for msg in conversation_history[-6:]  # Last 6 messages for context
    ])
    
    system_prompt = """あなたはベトナム人の日本語学習者（高校生または大学生）を演じています。

【キャラクター設定】
- 日本語レベル: N3〜N4程度（基本的な会話はできるが、複雑な表現は難しい）
- 性格: 少し内向的で、先生に対して緊張している
- 特徴:
  * 文法を間違えることを恐れている
  * 言いたいことがあっても、うまく言葉にできないことがある
  * 「えっと」「あの」などの言いよどみを使う
  * 簡単な言葉を選んで話す
  * 時々、文法的に不完全な文を使う
  * 先生が優しく接してくれると、少しずつ心を開く

【応答ルール】
1. 必ず「学生:」で始めてください
2. 1〜3文程度で短く返答してください
3. 状況に応じた感情を表現してください（緊張、感謝、困惑など）
4. 先生の対応に応じてリアクションを変えてください：
   - 優しい対応 → 少し安心して話しやすくなる
   - 厳しい対応 → より緊張して言葉が出にくくなる
5. 自然なベトナム人学生らしい反応をしてください"""

    user_prompt = f"""【シナリオ】
{scenario.title}
{scenario.description}

【これまでの会話】
{history_text}

【先生の最新メッセージ】
先生: {teacher_message}

上記の先生のメッセージに対して、ベトナム人学生として自然に返答してください。
「学生:」で始めて、1〜3文で返答してください。"""

    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,  # Higher for more natural variation
            max_tokens=200,
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Ensure it starts with 学生:
        if not reply.startswith("学生:"):
            reply = f"学生: {reply}"
        
        return reply
        
    except Exception as exc:
        raise HTTPException(
            status_code=500, 
            detail=f"AI service error (student response): {exc}"
        ) from exc


# ============================================
# 2. EVALUATE TEACHER RESPONSE
# ============================================

async def evaluate_teacher_response(
    scenario: Any,
    conversation_history: List[Dict],
    teacher_message: str,
) -> ScoreBreakdown:
    """
    Đánh giá câu trả lời của giáo viên theo 3 tiêu chí độc lập (0-100):
    - sincerity (本音度): Độ chân thành, gần gũi
    - appropriateness (適切さ): Độ phù hợp với tình huống
    - relevance (関連性): Độ liên quan đến vấn đề
    """
    
    # Build conversation context
    history_text = "\n".join([
        f"{'学生' if msg['role'] == 'student' else '先生'}: {msg['content']}"
        for msg in conversation_history[-4:]  # Last 4 messages
    ])
    
    system_prompt = """あなたは日本語教育の専門家です。教師の返答を評価してください。

【評価基準】各項目は0〜100点で独立して評価します。

1. 本音度 (sincerity): 0-100
   - 学生に対して心から向き合っているか
   - 表面的でなく、真摯な対応か
   - 学生が「この先生なら話せる」と感じられるか

2. 適切さ (appropriateness): 0-100
   - 状況に合った言葉遣いか
   - 学生の日本語レベルに配慮しているか
   - 威圧的でなく、安心感を与えるか

3. 関連性 (relevance): 0-100
   - 学生の発言や状況に対して的確に応答しているか
   - 話題から逸れていないか
   - 学生の本当の問題に向き合っているか

【出力形式】
必ず以下のJSON形式のみで返答してください：
{"sincerity": 数値, "appropriateness": 数値, "relevance": 数値}"""

    user_prompt = f"""【シナリオ】
{scenario.title}: {scenario.description}

【会話履歴】
{history_text}

【評価対象の先生の返答】
先生: {teacher_message}

上記の先生の返答を評価し、JSON形式で点数を出力してください。"""

    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # Lower for more consistent scoring
            max_tokens=100,
        )
        
        result_text = response.choices[0].message.content.strip()
        scores_data = parse_json_response(result_text)
        
        return ScoreBreakdown(
            sincerity=max(0, min(100, int(scores_data.get("sincerity", 50)))),
            appropriateness=max(0, min(100, int(scores_data.get("appropriateness", 50)))),
            relevance=max(0, min(100, int(scores_data.get("relevance", 50)))),
        )
        
    except json.JSONDecodeError as exc:
        # Fallback scores if parsing fails
        return ScoreBreakdown(sincerity=60, appropriateness=60, relevance=60)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error (evaluation): {exc}"
        ) from exc


# ============================================
# 3. GENERATE SESSION FEEDBACK
# ============================================

async def generate_session_feedback(
    scenario: Any,
    conversation_history: List[Dict],
    all_scores: List[Dict],
) -> SessionFeedback:
    """
    Tạo feedback chi tiết khi kết thúc session:
    - summary: Tóm tắt tổng quan
    - strengths: Điểm mạnh (list)
    - improvements: Điểm cần cải thiện (list)
    - suggestions: Gợi ý cho lần sau (list)
    """
    
    # Calculate average scores
    if all_scores:
        avg_sincerity = sum(s["sincerity"] for s in all_scores) / len(all_scores)
        avg_appropriateness = sum(s["appropriateness"] for s in all_scores) / len(all_scores)
        avg_relevance = sum(s["relevance"] for s in all_scores) / len(all_scores)
    else:
        avg_sincerity = avg_appropriateness = avg_relevance = 50
    
    # Build full conversation
    full_conversation = "\n".join([
        f"{'学生' if msg['role'] == 'student' else '先生'}: {msg['content']}"
        for msg in conversation_history
    ])
    
    system_prompt = """あなたは日本語教育の専門家です。教師の対話練習セッションを総括してください。

【出力形式】
必ず以下のJSON形式で返答してください：
{
    "summary": "全体の評価を2〜3文で",
    "strengths": ["良かった点1", "良かった点2"],
    "improvements": ["改善点1", "改善点2"],
    "suggestions": ["次回へのアドバイス1", "次回へのアドバイス2"]
}

【注意】
- 日本語で回答してください
- 具体的で実践的なフィードバックを提供してください
- 励ましの言葉も含めてください"""

    user_prompt = f"""【シナリオ】
{scenario.title}

【会話全文】
{full_conversation}

【平均スコア】
- 本音度: {avg_sincerity:.1f}/100
- 適切さ: {avg_appropriateness:.1f}/100
- 関連性: {avg_relevance:.1f}/100

【対話回数】
{len(all_scores)}回

上記のセッションを総括し、JSON形式でフィードバックを出力してください。"""

    try:
        response = client.chat.completions.create(
            model=get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.6,
            max_tokens=500,
        )
        
        result_text = response.choices[0].message.content.strip()
        feedback_data = parse_json_response(result_text)
        
        return SessionFeedback(
            summary=feedback_data.get("summary", "セッションを完了しました。"),
            strengths=feedback_data.get("strengths", ["対話を最後まで続けました"]),
            improvements=feedback_data.get("improvements", ["より具体的な質問を心がけましょう"]),
            suggestions=feedback_data.get("suggestions", ["学生の気持ちに寄り添う言葉を増やしましょう"]),
        )
        
    except json.JSONDecodeError:
        # Fallback feedback if parsing fails
        return SessionFeedback(
            summary=f"セッションを完了しました。{len(all_scores)}回の対話を行いました。",
            strengths=["対話を最後まで続けることができました"],
            improvements=["より具体的な質問を心がけましょう"],
            suggestions=["学生の気持ちに寄り添う言葉を増やしましょう"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error (feedback): {exc}"
        ) from exc

