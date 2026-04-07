import os
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config import HEADLESS, BROWSER_TIMEOUT, SCREENSHOT_PATH

class BrowserManager:
    """Wrapper for Playwright to handle browser automation."""
    
    def __init__(self, headless: bool = HEADLESS):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """Initialize the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless
            # channel="chrome" # Uncomment if you want to use your local Chrome
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()

    async def stop(self):
        """Cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str):
        """Navigate to a URL."""
        await self.page.goto(url, timeout=BROWSER_TIMEOUT)

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
