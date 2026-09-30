from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from .config import get_settings
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import Plan, User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def render_error(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(request=request, name="index.html", context={"error": message}, status_code=status_code)


def admin_authorized(x_admin_key: Optional[str]) -> bool:
    configured = get_settings().admin_key
    return not configured or x_admin_key == configured


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return render_error(request, str(exc), 422)

    try:
        workout_plan = generate_workout_gemini(data.username, data.age, data.weight, data.goal, data.intensity)
        nutrition_tip = generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:
        return render_error(request, str(exc), 503)

    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user is None:
        user = User(
            user_id=data.user_id, username=data.username, age=data.age,
            weight=data.weight, goal=data.goal, intensity=data.intensity,
        )
        db.add(user)
        db.flush()
    else:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    if user.plan is None:
        user.plan = Plan(original_plan=workout_plan, nutrition_tip=nutrition_tip)
    else:
        user.plan.original_plan = workout_plan
        user.plan.nutrition_tip = nutrition_tip
        user.plan.updated_plan = None
        user.plan.feedback = None
        user.plan.updated_at = None

    db.commit()
    db.refresh(user)
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": user.plan,
            "message": "Your 7-day FitBuddy plan has been generated.",
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except Exception as exc:
        return render_error(request, str(exc), 422)

    user = db.scalar(select(User).options(joinedload(User.plan)).where(User.user_id == data.user_id))
    if user is None or user.plan is None:
        return render_error(request, "No saved plan was found for that User ID.", 404)

    try:
        revised = update_workout_plan(user.plan.original_plan, data.feedback, user.goal, user.intensity)
        tip = generate_nutrition_tip_with_flash(user.goal)
    except Exception as exc:
        return render_error(request, str(exc), 503)

    user.plan.updated_plan = revised
    user.plan.feedback = data.feedback
    user.plan.nutrition_tip = tip
    user.plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": user.plan,
            "message": "Your feedback was applied and the plan was updated.",
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db), x_admin_key: Optional[str] = Header(default=None)):
    if not admin_authorized(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    users = db.scalars(select(User).options(joinedload(User.plan)).order_by(User.created_at.desc())).unique().all()
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": users})


@router.get("/api/users")
def api_users(db: Session = Depends(get_db), x_admin_key: Optional[str] = Header(default=None)):
    if not admin_authorized(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    users = db.scalars(select(User).options(joinedload(User.plan)).order_by(User.created_at.desc())).unique().all()
    return [
        {
            "user_id": u.user_id, "username": u.username, "age": u.age,
            "weight": u.weight, "goal": u.goal, "intensity": u.intensity,
            "has_updated_plan": bool(u.plan and u.plan.updated_plan),
        }
        for u in users
    ]


@router.get("/api/users/{user_id}")
def api_user(user_id: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).options(joinedload(User.plan)).where(User.user_id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user": {
            "user_id": user.user_id, "username": user.username, "age": user.age,
            "weight": user.weight, "goal": user.goal, "intensity": user.intensity,
        },
        "plan": {
            "original_plan": user.plan.original_plan if user.plan else None,
            "updated_plan": user.plan.updated_plan if user.plan else None,
            "nutrition_tip": user.plan.nutrition_tip if user.plan else None,
            "feedback": user.plan.feedback if user.plan else None,
        },
    }


@router.delete("/api/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), x_admin_key: Optional[str] = Header(default=None)):
    if not admin_authorized(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted", "user_id": user_id}


@router.get("/health")
def health():
    settings = get_settings()
    return JSONResponse({"status": "ok", "gemini_configured": bool(settings.gemini_api_key)})
