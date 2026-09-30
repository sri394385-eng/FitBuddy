from .config import get_settings
from .gemini_client import generate_text


def update_workout_plan(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    settings = get_settings()
    prompt = f"""
You are updating an existing FitBuddy 7-day workout plan.
Goal: {goal}
Intensity: {intensity}

Original plan:
{original_plan}

User feedback:
{feedback}

Create a revised 7-day plan that incorporates the feedback where reasonable.
Keep the same clear Day 1-Day 7 structure, include warm-up, main workout, and recovery/cool-down guidance.
Do not blindly follow unsafe requests. Do not diagnose or treat medical conditions.
Return plain text, not a markdown table.
"""
    return generate_text(prompt, settings.gemini_workout_model)
