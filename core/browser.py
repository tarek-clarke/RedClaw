import os
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config import HEADLESS, BROWSER_TIMEOUT, SCREENSHOT_PATH, SESSIONS_DIR
from core.safety_policy import SafetyPolicy

class BrowserManager:
    """Wrapper for Playwright to handle browser automation with persistent session support."""
    
    def __init__(self, headless: bool = HEADLESS, session_name: str = "default"):
        self.headless = headless
        self.session_name = session_name
        self.user_data_dir = os.path.join(SESSIONS_DIR, self.session_name)
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        self.playwright = None
        self.browser = None # For context-less sessions if needed
        self.context = None # Main persistent context
        self.page = None

    async def start(self):
        """Initialize the browser with persistent context."""
        self.playwright = await async_playwright().start()
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def stop(self):
        """Cleanup."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str):
        """Navigate to a URL and check for safety/captchas."""
        await self.page.goto(url, timeout=BROWSER_TIMEOUT)
        
        # Immediate CAPTCHA check after any navigation (V2.6)
        safety = SafetyPolicy()
        accessibility_tree = await self.get_accessibility_tree()
        if safety.is_captcha_present(accessibility_tree):
            print(f"\n[REDCLAW] NAVIGATION WARNING: CAPTCHA detected. Pausing for human intervention.")
            await self.wait_for_user()

    async def take_screenshot(self, filename: str = "observation.png") -> str:
        """Capture screenshot for visual observation."""
        path = os.path.join(SCREENSHOT_PATH, filename)
        await self.page.screenshot(path=path, full_page=False)
        return path

    async def get_accessibility_tree(self) -> str:
        """Extract DOM information for reasoning."""
        # Simple placeholder for accessibility tree
        snapshot = await self.page.accessibility.snapshot()
        return str(snapshot)

    async def click(self, selector: str):
        """Perform click action."""
        await self.page.click(selector, timeout=5000)

    async def type(self, selector: str, text: str):
        """Perform type action."""
        await self.page.fill(selector, text, timeout=5000)

    async def wait_for_user(self):
        """Pause the agent and wait for manual intervention."""
        # This is a basic way to wait for the user to continue via terminal
        print("\n[REDCLAW] HITL - PLEASE MANUALLY INTERVENE IN THE BROWSER...")
        print("[REDCLAW] TYPE 'done' IN THE TERMINAL TO CONTINUE...")
        while True:
            response = await asyncio.to_thread(input, "RedClaw> ")
            if response.lower() == "done":
                break
