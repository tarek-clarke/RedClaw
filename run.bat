@echo off
echo [REDCLAW] Starting RedClaw execution on Windows...

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [REDCLAW] Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: 2. Virtual Environment Setup
if not exist "venv" (
    echo [REDCLAW] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

:: 3. Dependency Installation
echo [REDCLAW] Syncing dependencies...
pip install -r requirements.txt -q

:: 4. Playwright Setup
echo [REDCLAW] Ensuring browser drivers are present...
playwright install chromium

:: 5. Local Data Validation
if not exist "user_profile.json" (
    echo [REDCLAW] Warning: 'user_profile.json' not found. Please create it from 'user_profile.example.json'.
)

if not exist "resume.pdf" (
    echo [REDCLAW] Warning: 'resume.pdf' not found.
)

:: 6. Run Agent
if "%~1"=="" (
    set /p GOAL="[REDCLAW] Enter your job application goal: "
    python main.py --goal "%GOAL%"
) else (
    echo [REDCLAW] Running with arguments: %*
    python main.py %*
)

pause
