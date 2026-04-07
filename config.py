import os
from dotenv import load_dotenv

load_dotenv()

# LM Studio Configuration (Clean Config V3.2)
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")

# RedClaw Agent Settings
# 💡 In LM Studio, ensure you are using a model with 'Vision' or 'VL' in the name for multimodal tasks.
DEFAULT_MODEL_VISION = os.getenv("DEFAULT_MODEL_VISION", "openai/gpt-oss-20b")
DEFAULT_MODEL_REASONING = os.getenv("DEFAULT_MODEL_REASONING", "openai/gpt-oss-20b")
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"

print(f"[REDCLAW] [CONFIG] Vision Model: {DEFAULT_MODEL_VISION}")
if "vision" not in DEFAULT_MODEL_VISION.lower() and "vl" not in DEFAULT_MODEL_VISION.lower() and "oss" not in DEFAULT_MODEL_VISION.lower():
    print(f"[REDCLAW] [WARNING] Your model name '{DEFAULT_MODEL_VISION}' does not appear to support Vision. Form-filling may fail.")

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
