import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger(__name__)

class SyllabusTopicItem(BaseModel):
    name: str = Field(..., min_length=1)
    est_hours: float = Field(..., gt=0)
    difficulty: int = Field(..., ge=1, le=5)
    weight: int = Field(..., ge=1, le=5)

class SyllabusParseResult(BaseModel):
    topics: List[SyllabusTopicItem]

class MCQItem(BaseModel):
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_index: int = Field(..., ge=0, le=3)
    explanation: str
    subtopic: str

class QuizGenResult(BaseModel):
    questions: List[MCQItem]


def get_anthropic_client():
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    except Exception as e:
        logger.error(f"Failed to instantiate Anthropic client: {e}")
        return None


async def parse_syllabus_with_llm(syllabus_text: str) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Parses raw syllabus text into structured topics using Anthropic API.
    Returns: (success: bool, topics: List[Dict], error_message: str)
    """
    client = get_anthropic_client()
    if not client:
        return (False, [], "Anthropic API key is not configured. Please set ANTHROPIC_API_KEY in .env.")

    prompt = f"""
You are an expert curriculum parser. Extract structured study topics from the syllabus text below.
Respond ONLY with valid, raw JSON adhering strictly to this schema:
{{
  "topics": [
    {{
      "name": "Topic Title",
      "est_hours": 3.0,
      "difficulty": 3,
      "weight": 4
    }}
  ]
}}

Rules:
- est_hours: estimated study hours (positive float, e.g. 1.5 - 10.0)
- difficulty: integer 1 to 5 (1 = very easy, 5 = very hard)
- weight: integer 1 to 5 (1 = low exam weight, 5 = high exam weight)
- Do NOT include any markdown formatting, triple backticks, or intro/outro text. ONLY valid JSON.

Syllabus Text:
{syllabus_text}
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        content_text = response.content[0].text.strip()

        # Clean JSON markdown fences if present
        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
            content_text = content_text.strip()

        data = json.loads(content_text)
        validated = SyllabusParseResult.model_validate(data)
        
        parsed_topics = [t.model_dump() for t in validated.topics]
        return (True, parsed_topics, "")
    except json.JSONDecodeError as e:
        logger.error(f"Syllabus LLM JSON decode error: {e}")
        return (False, [], f"AI output was malformed JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Syllabus LLM API error: {e}")
        return (False, [], f"LLM API Error: {str(e)}")


async def generate_mcqs_with_llm(topic_name: str, subject_name: str) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Generates 5 multiple choice questions for a topic using Anthropic API.
    Returns: (success: bool, questions: List[Dict], error_message: str)
    """
    client = get_anthropic_client()
    if not client:
        return (False, [], "Anthropic API key is not configured. Please set ANTHROPIC_API_KEY in .env.")

    prompt = f"""
Generate 5 high-quality multiple choice questions (MCQs) to test student mastery on topic: "{topic_name}" in subject: "{subject_name}".
Respond ONLY with valid raw JSON adhering strictly to this schema:
{{
  "questions": [
    {{
      "question": "What is ...?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Option A is correct because...",
      "subtopic": "Subtopic Name"
    }}
  ]
}}

Rules:
- Generate exactly 5 questions.
- options must contain exactly 4 distinct choices.
- correct_index must be 0, 1, 2, or 3.
- Do NOT include markdown codeblocks or extra text. Output JSON only.
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        content_text = response.content[0].text.strip()

        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
            content_text = content_text.strip()

        data = json.loads(content_text)
        validated = QuizGenResult.model_validate(data)
        
        qs = [q.model_dump() for q in validated.questions]
        return (True, qs, "")
    except Exception as e:
        logger.error(f"Quiz MCQ Gen error: {e}")
        return (False, [], f"AI Quiz Generation error: {str(e)}")
