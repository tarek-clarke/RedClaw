import os
from dotenv import load_dotenv

load_dotenv()

# LM Studio Configuration
LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio") # dummy key for local

# RedClaw Agent Settings
DEFAULT_MODEL_VISION = os.getenv("DEFAULT_MODEL_VISION", "gemma-4")
DEFAULT_MODEL_REASONING = os.getenv("DEFAULT_MODEL_REASONING", "gpt-oss-20b")

# Browser Settings
HEADLESS = False # We want headed mode for HITL
BROWSER_TIMEOUT = 30000 # 30 seconds
SCREENSHOT_PATH = "screenshots"

# Ensure directories exist
os.makedirs(SCREENSHOT_PATH, exist_ok=True)
