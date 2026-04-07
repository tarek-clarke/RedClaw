import os
from dotenv import load_dotenv

load_dotenv()

# LM Studio Configuration (Synced with V3.1 Screenshot)
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://100.119.120.114:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")

# RedClaw Agent Settings
DEFAULT_MODEL_VISION = os.getenv("DEFAULT_MODEL_VISION", "openai/gpt-oss-20b")
DEFAULT_MODEL_REASONING = os.getenv("DEFAULT_MODEL_REASONING", "openai/gpt-oss-20b")
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"

# Browser Settings
HEADLESS = False # We want headed mode for HITL
BROWSER_TIMEOUT = 30000 # 30 seconds
SCREENSHOT_PATH = "screenshots"
LOG_DIR = "logs"
SESSIONS_DIR = ".sessions"

# Safety Policies
ALLOWED_DOMAINS = ["greenhouse.io", "lever.co", "workday.com", "ashbyhq.com", "linkedin.com", "github.com", "google.com"]
PAUSE_BEFORE_SUBMIT = True
PAUSE_BEFORE_LOGIN = True
PAUSE_BEFORE_FILE_UPLOAD = True

# Ensure directories exist
os.makedirs(SCREENSHOT_PATH, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
