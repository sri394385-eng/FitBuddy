import os
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.sqlite3"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app
from app import routes


def fake_plan(*args, **kwargs):
    return "Day 1: Full body\nWarm-up: 5 minutes\nMain: Squat 3x10\nCooldown: 5 minutes"


def fake_tip(*args, **kwargs):
    return "Drink water regularly and include a protein-rich food with meals."


def fake_update(*args, **kwargs):
    return "Day 1: Updated full body\nWarm-up: 5 minutes\nMain: Brisk walk 20 minutes\nCooldown: 5 minutes"


routes.generate_workout_gemini = fake_plan
routes.generate_nutrition_tip_with_flash = fake_tip
routes.update_workout_plan = fake_update

def test_home():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_generate_and_fetch_user():
    with TestClient(app) as client:
        response = client.post("/generate-workout", data={
        "username": "Test User", "user_id": "TEST001", "age": "22",
        "weight": "65", "goal": "general wellness", "intensity": "medium"
    })
        assert response.status_code == 200
        assert "Day 1" in response.text

        response = client.get("/api/users/TEST001")
        assert response.status_code == 200
        assert response.json()["user"]["username"] == "Test User"


def test_feedback_update():
    with TestClient(app) as client:
        response = client.post("/submit-feedback", data={
        "user_id": "TEST001", "feedback": "Include more cardio."
    })
        assert response.status_code == 200
        assert "Updated Plan" in response.text


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
