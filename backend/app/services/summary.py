import logging
from typing import Dict, Any, Optional
from app.services.llm import get_anthropic_client

logger = logging.getLogger(__name__)

def generate_daily_summary_text(stats: Dict[str, Any]) -> str:
    """
    Phrases a daily summary. Uses Anthropic LLM if key is present, otherwise returns deterministic fallback text.
    Stats dictionary contains pre-calculated deterministic metrics.
    """
    completed_hrs = round(stats.get("completed_minutes", 0) / 60.0, 1)
    planned_hrs = round(stats.get("planned_minutes", 0) / 60.0, 1)
    missed_count = stats.get("missed_count", 0)
    topics_completed = stats.get("topics_completed_today", 0)
    upcoming_exam = stats.get("upcoming_exam_title", "None")
    exam_readiness = stats.get("upcoming_exam_readiness", "N/A")

    fallback = (
        f"Today you completed {completed_hrs} hours out of {planned_hrs} planned study hours across {topics_completed} topics. "
        f"You missed {missed_count} planned sessions. "
        f"Next upcoming exam: '{upcoming_exam}' with current readiness score of {exam_readiness}%. "
        f"Keep up the focused effort!"
    )

    client = get_anthropic_client()
    if not client:
        return fallback

    prompt = f"""
Convert the following pre-calculated study statistics into a friendly, encouraging, 2-3 sentence daily study summary for a student:
- Study time completed today: {completed_hrs} hours (planned: {planned_hrs} hours)
- Sessions missed today: {missed_count}
- Topics completed today: {topics_completed}
- Upcoming Exam: {upcoming_exam}
- Exam Readiness Score: {exam_readiness}%

Requirements:
- Keep it concise, motivational, and conversational.
- Do NOT alter any of the numerical statistics provided.
- Do NOT output extra bullet points or preamble.
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Daily summary LLM error: {e}")
        return fallback


def generate_weekly_summary_text(stats: Dict[str, Any]) -> str:
    """
    Phrases a weekly summary. Uses Anthropic LLM if key is present, otherwise returns deterministic fallback text.
    """
    completed_hrs = round(stats.get("weekly_completed_minutes", 0) / 60.0, 1)
    planned_hrs = round(stats.get("weekly_planned_minutes", 0) / 60.0, 1)
    completion_rate = stats.get("weekly_completion_rate", 0.0)
    subject_progress = stats.get("subject_progress_summary", "")

    fallback = (
        f"This week you completed {completed_hrs} hours of study out of {planned_hrs} hours planned "
        f"({completion_rate}% completion rate). {subject_progress} "
        f"Great progress! Review your schedule for the upcoming week to stay on track."
    )

    client = get_anthropic_client()
    if not client:
        return fallback

    prompt = f"""
Convert the following pre-calculated weekly study statistics into an insightful 3-4 sentence weekly performance summary for a student:
- Total completed study hours this week: {completed_hrs}h (Planned: {planned_hrs}h)
- Completion rate: {completion_rate}%
- Subject progress details: {subject_progress}

Requirements:
- Direct, constructive, and actionable tone.
- Do NOT alter the numerical metrics.
- Output ONLY the final summary text.
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Weekly summary LLM error: {e}")
        return fallback
