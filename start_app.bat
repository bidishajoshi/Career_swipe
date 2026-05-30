@echo off
setlocal
cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
  echo Project virtual environment was not found at .\venv\Scripts\python.exe
  echo Create it or reinstall dependencies before starting the app.
  exit /b 1
)

set PYTHONDONTWRITEBYTECODE=1
set FLASK_APP=app.py

echo Starting CareerSwipe at http://127.0.0.1:5000
".\venv\Scripts\python.exe" -m flask run --host 127.0.0.1 --port 5000
