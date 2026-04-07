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
        """Navigate to a URL and check for safety/captchas with performance optimization."""
        print(f"[REDCLAW] Navigating to target URL: {url}")
        try:
            # V4.5 Optimization: Wait for DOM instead of full network idle to avoid tracker hangs
            await self.page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
            # Give short extra stabilization time
            await asyncio.sleep(2)
        except Exception as e:
            print(f"[REDCLAW] Navigation Warning (Timeout or Error): {str(e)}")
        
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
        """Extract form-aware DOM snapshot for text-only LLM reasoning (V6.0)."""
        import json
        try:
            tree_data = await self.page.evaluate('''() => {
                const results = { inputs: [], buttons: [], links: [], headings: [], page_title: document.title, url: location.href };
                
                // Extract all form inputs
                document.querySelectorAll('input, select, textarea').forEach((el, i) => {
                    const label = el.closest('label')?.innerText 
                        || document.querySelector('label[for="' + el.id + '"]')?.innerText
                        || el.getAttribute('aria-label')
                        || el.getAttribute('placeholder')
                        || el.getAttribute('name')
                        || ('unnamed_field_' + i);
                    results.inputs.push({
                        index: i,
                        tag: el.tagName.toLowerCase(),
                        type: el.getAttribute('type') || 'text',
                        name: el.getAttribute('name') || '',
                        id: el.id || '',
                        label: label.trim().slice(0, 80),
                        placeholder: el.getAttribute('placeholder') || '',
                        value: el.value || '',
                        required: el.required,
                        selector: el.id ? '#' + el.id : (el.name ? '[name="' + el.name + '"]' : 'input:nth-of-type(' + (i+1) + ')')
                    });
                });
                
                // Extract all buttons
                document.querySelectorAll('button, [role="button"], input[type="submit"]').forEach((el, i) => {
                    results.buttons.push({
                        index: i,
                        text: (el.innerText || el.value || '').trim().slice(0, 50),
                        type: el.getAttribute('type') || 'button',
                        selector: el.id ? '#' + el.id : 'button:nth-of-type(' + (i+1) + ')'
                    });
                });
                
                // Extract page headings for context
                document.querySelectorAll('h1, h2, h3').forEach(el => {
                    results.headings.push(el.innerText.trim().slice(0, 100));
                });
                
                return results;
            }''')
            
            summary = f"PAGE: {tree_data.get('page_title', 'Unknown')} ({tree_data.get('url', '')})\n"
            summary += f"HEADINGS: {', '.join(tree_data.get('headings', []))}\n\n"
            
            summary += "FORM FIELDS:\n"
            for inp in tree_data.get('inputs', []):
                filled = f" [FILLED: '{inp['value']}']" if inp['value'] else " [EMPTY]"
                req = " *REQUIRED*" if inp.get('required') else ""
                summary += f"  [{inp['index']}] {inp['label']} (type={inp['type']}, selector=\"{inp['selector']}\"){filled}{req}\n"
            
            summary += "\nBUTTONS:\n"
            for btn in tree_data.get('buttons', []):
                summary += f"  [{btn['index']}] \"{btn['text']}\" (selector=\"{btn['selector']}\")\n"
            
            return summary
        except Exception as e:
            print(f"[REDCLAW] DOM Scan Warning: {str(e)}")
            return "ERROR: Could not scan page DOM."

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
