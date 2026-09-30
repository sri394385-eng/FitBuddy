# FitBuddy – AI Fitness Plan Generator

A FastAPI + SQLite + Jinja2 fitness planner that uses Gemini through the **Gemini REST API**.

## Windows 7 / Python 3.8 version

This version is specifically prepared for older Windows systems. It does **not** require the `google-genai` Python package. Instead, the app calls the Gemini REST API using `httpx`, so the Python environment only needs packages that support Python 3.8.

> Note: Google's newer Gemini Python SDK requires a newer Python version. This Windows 7 build therefore uses the REST API as a compatibility workaround. The legacy `google-generativeai` SDK is not used.

## Project structure

```text
FitBuddy/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
├── static/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Windows 7 setup

Open PowerShell/Command Prompt in the `FitBuddy` folder.

### 1. Create the virtual environment

If `.venv` already exists, you can keep using it. Otherwise:

```powershell
C:\Users\Admin\AppData\Local\Programs\Python\Python38\python.exe -m venv .venv
```

If your Python 3.8 path is different, replace the path with your actual `python.exe` path.

### 2. Install dependencies

If `.venv` is one folder above `FitBuddy`, as in the original setup:

```powershell
..\.venv\Scripts\python.exe -m pip install --upgrade pip
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `.venv` is inside the current `FitBuddy` folder, use:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configure Gemini

Copy `.env.example` to `.env`.

Put your Gemini API key in `.env`:

```env
GEMINI_API_KEY=your_actual_key_here
```

### 4. Run the app

For the original folder arrangement where `.venv` is in `FitBuddy_Project` and the application is in `FitBuddy`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

You should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open:

- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/view-all-users
- http://localhost:8000/health

### 5. Run tests

```powershell
..\.venv\Scripts\python.exe -m pytest -q
```

## Gemini REST API

The app sends a request to the Gemini REST endpoint directly using `httpx`. No Gemini Python SDK is required.

The model can be changed in `.env`:

```env
GEMINI_WORKOUT_MODEL=gemini-2.5-flash
GEMINI_TIP_MODEL=gemini-2.5-flash
```

## Important

This is a college/demo wellness application, not a medical diagnosis system. Users should seek professional medical advice for injuries, illness, or medical conditions.
