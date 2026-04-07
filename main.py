import json
import os
import asyncio
import click
from core.browser import BrowserManager
from core.llm import LLMManager
from core.agent import RedClawAgent
from core.resume import ResumeManager
from core.preflight import PreflightManager
from config import LM_STUDIO_HOST, DEFAULT_MODEL_VISION

def load_profile(path: str = "user_profile.json") -> dict:
    """Load personal profile if it exists."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    print(f"[REDCLAW] Profile not found at {path}. Using empty profile.")
    return {}

@click.command()
@click.option("--goal", default="Find and apply for senior ML roles", help="The goal for the agent.")
@click.option("--url", default=None, help="Initial URL (skips discovery if provided).")
@click.option("--resume", default="resume.pdf", help="Path to your PDF resume.")
@click.option("--dry-run", is_flag=True, help="Run without clicking final submit.")
@click.option("--session", default="default", help="Persistent browser session name.")
@click.option("--url-file", default=None, help="Path to a text file containing job URLs (one per line).")
@click.option("--discover", is_flag=True, help="Search for new jobs based on your profile.")
def main(
    goal: str = "Find and apply for senior ML roles", 
    url: str = None, 
    resume: str = "resume.pdf", 
    dry_run: bool = False, 
    session: str = "default", 
    url_file: str = None, 
    discover: bool = False
):
    """RedClaw: Local Browser Agent for AMD users."""
    
    # Load user data
    print("[REDCLAW] [BOOT] Loading user_profile.json...")
    profile = load_profile()
    print("[REDCLAW] [BOOT] Extracting text from resume...")
    resume_text = ResumeManager.extract_text(resume) or ""
    print(f"[REDCLAW] [BOOT] Resume loaded ({len(resume_text)} chars).")
    
    # 1. Handle Batch Mode (URL File)
    if url_file:
        if os.path.exists(url_file):
            print(f"[REDCLAW] Batch Mode: Loading links from {url_file}...")
            with open(url_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            for i, target_url in enumerate(urls):
                print(f"\n[REDCLAW] [BOOT] Launching Job {i+1}/{len(urls)}: {target_url}")
                asyncio.run(run_redclaw(goal, target_url, resume_text, profile, dry_run, session, False))
            return
        else:
            print(f"[REDCLAW] Error: URL file {url_file} not found.")
            return

    # 2. Standard Single-Run Mode
    asyncio.run(run_redclaw(goal, url, resume_text, profile, dry_run, session, discover))

async def run_redclaw(goal: str, url: str, resume_text: str, profile: dict, dry_run: bool, session_name: str, discover: bool):
    # 1. Setup
    print(f"\n[REDCLAW] Connecting to LM Studio at {LM_STUDIO_HOST}...")
    
    if dry_run:
        print("[REDCLAW] DRY-RUN MODE ACTIVE: No submissions will be made.")

    browser = BrowserManager(headless=False, session_name=session_name)
    llm = LLMManager()
    preflight = PreflightManager(llm, resume_text=resume_text, profile_data=profile)
    agent = RedClawAgent(browser, llm, resume_text=resume_text, profile_data=profile, dry_run=dry_run)
    
    try:
        print(f"[REDCLAW] Initializing browser (session: {session_name})...")
        await browser.start()
        
        # 2. Discovery Mode (V2.3 - Autostart if no URL)
        if (discover or not url):
            print(f"[REDCLAW] No URL provided. Launching Job Discovery Mode for: {goal}...")
            from core.discovery import JobDiscovery
            discovery = JobDiscovery(browser, llm, preflight)
            ranked_jobs = await discovery.run_discovery(goal=goal)
            
            if not ranked_jobs:
                print("[REDCLAW] No jobs found during discovery. Try a different goal.")
                return

            print("\n[REDCLAW] DISCOVERY REPORT (Top Recommendations):")
            for i, job in enumerate(ranked_jobs[:5]):
                print(f"{i+1}. {job['title']} at {job['company']} (Score: {job['score']}/100)")
                print(f"   Fit: {job['recommendation']}")
            
            print("\n[REDCLAW] Enter the number of the job you want to target (or 'none'):")
            choice = await asyncio.to_thread(input, "RedClaw Target> ")
            if choice.isdigit() and int(choice) <= len(ranked_jobs):
                url = ranked_jobs[int(choice)-1]['link']
                print(f"[REDCLAW] Targeting: {url}")
            else:
                print("[REDCLAW] Task ended by user.")
                return

        # 3. Start Application Flow
        if url:
            print(f"[REDCLAW] Navigating to: {url}")
            await browser.navigate(url)
            await agent.run_task(goal)
        
    except Exception as e:
        print(f"\n[REDCLAW] CRITICAL ERROR: {str(e)}")
        print("[REDCLAW] BROWSER PROTECTED: Keeping session open for diagnosis.")
        await asyncio.to_thread(input, "Press Enter to close browser and exit...")
    finally:
        await browser.stop()

if __name__ == "__main__":
    main()
