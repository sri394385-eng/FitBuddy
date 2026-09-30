from .config import get_settings
from .gemini_client import generate_text


def generate_nutrition_tip_with_flash(goal: str) -> str:
    settings = get_settings()
    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.
Fitness goal: {goal}
Give one concise, practical nutrition or recovery tip that complements this goal.
Mention a simple food/hydration/recovery action when appropriate.
Avoid medical diagnosis, extreme dieting, or unsafe supplement advice.
Answer in 2-4 sentences.
"""
    return generate_text(prompt, settings.gemini_tip_model)
