import json
import os
import asyncio
import click
from core.browser import BrowserManager
from core.llm import LLMManager
from core.agent import RedClawAgent
from core.resume import ResumeManager
from config import LM_STUDIO_HOST, DEFAULT_MODEL_VISION

def load_profile(path: str = "user_profile.json") -> dict:
    """Load personal profile if it exists."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    print(f"[REDCLAW] Profile not found at {path}. Using empty profile.")
    return {}

@click.command()
@click.option("--goal", prompt="What task should RedClaw perform?", help="The goal for the agent.")
@click.option("--url", default="https://www.google.com", help="Initial URL.")
@click.option("--resume", default="resume.pdf", help="Path to your PDF resume.")
def main(goal: str, url: str, resume: str):
    """RedClaw: Local Browser Agent for AMD users."""
    
    # Load user data
    profile = load_profile()
    resume_text = ResumeManager.extract_text(resume) or ""
    
    asyncio.run(run_redclaw(goal, url, resume_text, profile))

async def run_redclaw(goal: str, url: str, resume_text: str, profile: dict):
    # 1. Setup
    print(f"\n[REDCLAW] Connecting to LM Studio at {LM_STUDIO_HOST}...")
    print(f"[REDCLAW] (If LM Studio is on another PC, update config.py with the PC's IP address)")
    
    browser = BrowserManager(headless=False)
    llm = LLMManager()
    agent = RedClawAgent(browser, llm, resume_text=resume_text, profile_data=profile)
    
    try:
        await browser.start()
        await browser.navigate(url)
        
        # 2. Start Task
        await agent.run_task(goal)
        
    finally:
        await browser.stop()

if __name__ == "__main__":
    main()
