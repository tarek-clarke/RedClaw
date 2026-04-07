#!/bin/bash

# RedClaw: Local One-Go Runner
set -e

echo "[REDCLAW] Starting RedClaw execution..."

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[REDCLAW] Error: Python 3 is not installed. Please install it to continue."
    exit 1
fi

# 2. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "[REDCLAW] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Dependency Installation
echo "[REDCLAW] Syncing dependencies..."
pip install -r requirements.txt -q

# 4. Playwright Setup
echo "[REDCLAW] Ensuring browser drivers are present..."
playwright install chromium

# 5. Local Data Validation
if [ ! -f "user_profile.json" ]; then
    echo "[REDCLAW] Warning: 'user_profile.json' not found. Please create it from 'user_profile.example.json'."
fi

if [ ! -f "resume.pdf" ]; then
    echo "[REDCLAW] Warning: 'resume.pdf' not found. Applications will not have resume data."
fi

# 6. Run Agent
read -p "[REDCLAW] Enter your job application goal (e.g., 'Apply for Y at X'): " GOAL
python3 main.py --goal "$GOAL"
