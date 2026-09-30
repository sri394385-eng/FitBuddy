from .config import get_settings
from .gemini_client import generate_text


def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    settings = get_settings()
    prompt = f"""
You are FitBuddy, a careful fitness-planning assistant.
Create a personalized 7-day wellness workout plan for:
Name: {username}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Preferred intensity: {intensity}

Return a clearly structured plan for Day 1 through Day 7.
For each day include:
- Focus
- Warm-up (5-10 minutes)
- Main workout with exercise name, sets/reps or duration, and rest
- Cool-down/recovery guidance

Adapt volume to the requested intensity. Include at least one recovery/rest-oriented day.
Do not diagnose medical conditions or prescribe treatment. Use practical, general wellness guidance.
Keep the answer easy to read in plain text and do not use a markdown table.
"""
    return generate_text(prompt, settings.gemini_workout_model)
