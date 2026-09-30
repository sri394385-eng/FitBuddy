"""Gemini REST client compatible with Python 3.8 / Windows 7.

This intentionally avoids the modern google-genai SDK because that SDK requires
newer Python versions. It calls the Gemini REST API directly with httpx instead.
"""
from typing import Optional

import httpx

from .config import get_settings


def generate_text(prompt: str, model: Optional[str] = None) -> str:
    """Generate text using Gemini's REST API.

    Returns a readable error when the API key is missing or the API request fails.
    """
    settings = get_settings()

    if not settings.gemini_api_key:
        return (
            "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file."
        )

    model_name = model or settings.gemini_workout_model
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = httpx.post(
            url,
            params={"key": settings.gemini_api_key},
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return "Gemini did not return a response. Please try again."

        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [part.get("text", "") for part in parts if part.get("text")]
        text = "\n".join(text_parts).strip()

        return text or "Gemini returned an empty response. Please try again."

    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("error", {}).get("message", str(exc))
        except Exception:
            detail = str(exc)
        return f"Gemini API error: {detail}"
    except Exception as exc:
        return f"Gemini request failed: {exc}"
