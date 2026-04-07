import asyncio
import os
from typing import Optional, Dict, Any, List
from core.browser import BrowserManager
from core.llm import LLMManager
from config import DEFAULT_MODEL_VISION

class RedClawAgent:
    """The brain of the RedClaw agent."""
    
    def __init__(self, browser: BrowserManager, llm: LLMManager, resume_text: str = "", profile_data: dict = None):
        self.browser = browser
        self.llm = llm
        self.resume_text = resume_text
        self.profile_data = profile_data or {}
        self.history = []

    async def run_task(self, goal: str):
        """Main loop: Observe -> Plan -> Act."""
        print(f"\n[REDCLAW] Starting Task: {goal}")
        
        while True:
            # 1. Observe
            screenshot_path = await self.browser.take_screenshot("current_state.png")
            accessibility_tree = await self.browser.get_accessibility_tree()
            
            # 2. Plan
            prompt = self._build_prompt(goal, accessibility_tree)
            response = self.llm.multimodal_completion(prompt, screenshot_path)
            
            print(f"\n[REDCLAW] Agent Decision: {response}")
            
            # 3. Safety Check: Never click "Submit" or "Apply" without HITL
            if any(key in response.upper() for key in ["SUBMIT", "APPLY", "FINISH"]):
                print("\n[REDCLAW] SAFETY TRIGGER: Application submission detected. Pausing for human review.")
                await self.browser.wait_for_user()
                # After user review, we let the agent continue or the user can manual click
                continue

            # 4. Handle HITL or Actions
            if "ASK_USER" in response or "PAUSE" in response:
                await self.browser.wait_for_user()
                continue
                
            if "COMPLETE" in response:
                print("\n[REDCLAW] Task successfully completed!")
                break
                
            # 5. Execute Action (Placeholder for real execution logic)
            # In a full impl, we'd parse and call await self.browser.click(selector), etc.
            await asyncio.sleep(2)

    def _build_prompt(self, goal: str, accessibility_tree: str) -> str:
        """Construct the prompt for the multi-modal model with resume context."""
        
        profile_summary = f"""
        NAME: {self.profile_data.get('full_name', 'Not Provided')}
        LINKS: {self.profile_data.get('links', {})}
        HIGHLIGHTS: {self.profile_data.get('key_highlights', [])}
        PHD FOCUS: {self.profile_data.get('phd_focus', 'Not Provided')}
        """

        return f"""
YOU ARE REDCLAW, A BROWSER ASSISTANT FOR AMD USERS.
YOUR GOAL: {goal}

USER PROFILE:
{profile_summary}

RESUME TEXT:
{self.resume_text[:2000]} # Limit for context window if needed

ACCESSIBILITY TREE:
{accessibility_tree}

OBSERVE THE SCREENSHOT AND DECIDE THE NEXT STEP.
AVAILABLE ACTIONS:
- CLICK(selector)
- TYPE(selector, text)
- NAVIGATION(url)
- ASK_USER("message") (Triggers HITL)
- COMPLETE()

INSTRUCTIONS FOR JOB APPLICATIONS:
1. USE THE RESUME AND PROFILE DATA TO FILL OUT FORMS.
2. IF YOU SEE A FIELD FOR "PHD" OR "ACHIEVEMENTS", HIGHLIGHT THE RESILIENT RAP FRAMEWORK.
3. IF YOU SEE A BUTTON TO "SUBMIT", "APPLY", OR "FINISH", DO NOT CLICK IT. INSTEAD, USE ASK_USER("Final review needed").
4. ALWAYS BE CONCISE IN FORM FIELDS.

NEXT ACTION:
"""
