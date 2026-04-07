import asyncio
import os
from typing import Optional, Dict, Any, List
from core.browser import BrowserManager
from core.llm import LLMManager
from core.audit_logger import AuditLogger
from core.safety_policy import SafetyPolicy
from config import DEFAULT_MODEL_VISION, DRY_RUN

class RedClawAgent:
    """The brain of the RedClaw agent."""
    
    def __init__(self, browser: BrowserManager, llm: LLMManager, resume_text: str = "", profile_data: dict = None, dry_run: bool = DRY_RUN):
        self.browser = browser
        self.llm = llm
        self.resume_text = resume_text
        self.profile_data = profile_data or {}
        self.dry_run = dry_run
        self.logger = AuditLogger()
        self.safety = SafetyPolicy()
        self.history = []

    async def run_task(self, goal: str):
        """Main loop: Plan Preview -> Observe -> Decide -> Act."""
        print(f"\n[REDCLAW] Starting Task: {goal}")
        self.logger.log("task_start", {"goal": goal, "dry_run": self.dry_run})
        
        # 1. Action Plan Preview (V2 Feature)
        plan = await self._generate_action_plan(goal)
        print(f"\n[REDCLAW] PROPOSED ACTION PLAN:\n{plan}")
        
        if not await self._get_human_approval(plan):
            print("\n[REDCLAW] Plan rejected. Exiting.")
            self.logger.log_approval(plan, False, "Terminated by user")
            return

        self.logger.log_approval(plan, True)

        while True:
            # 2. Observe
            screenshot_path = await self.browser.take_screenshot("current_state.png")
            accessibility_tree = await self.browser.get_accessibility_tree()
            
            # 3. Decide
            prompt = self._build_prompt(goal, accessibility_tree)
            response = self.llm.multimodal_completion(prompt, screenshot_path)
            
            print(f"\n[REDCLAW] Agent Decision: {response}")
            self.logger.log("decision", {"response": response, "screenshot": screenshot_path})
            
            # 4. Safety & HITL Check
            if self.safety.should_pause_before_action("DECISION", response):
                print(f"\n[REDCLAW] SAFETY TRIGGER: High-priority action detected. Pausing for review.")
                if self.dry_run:
                    print("[REDCLAW] (Dry-Run: Skipping potential submission)")
                    break
                await self.browser.wait_for_user()
                continue

            # 5. Handle Specialized Tools (ASK_USER)
            if "ASK_USER" in response or "ESC_HUMAN" in response:
                print("\n[REDCLAW] ESCALATION: Agent is requesting human assistance.")
                await self.browser.wait_for_user()
                continue
                
            if "COMPLETE" in response:
                print("\n[REDCLAW] Task successfully completed!")
                self.logger.log("task_complete", {})
                break
                
            # 6. Action Execution (Placeholder)
            await asyncio.sleep(2)

    async def _generate_action_plan(self, goal: str) -> str:
        """Generate a structured plan for the task before execution."""
        prompt = f"Generate a high-level step-by-step action plan to achieve this goal: {goal}. Focus on major milestones (e.g., Navigate, Detect Form, Fill, Pause for Submit)."
        messages = [{"role": "user", "content": prompt}]
        return self.llm.chat_completion(messages)

    async def _get_human_approval(self, plan: str) -> bool:
        """Request explicit human approval for the proposed plan."""
        print("\n[REDCLAW] Do you approve this plan? (yes/no/edit)")
        while True:
            response = await asyncio.to_thread(input, "RedClaw Approve> ")
            if response.lower() == "yes":
                return True
            if response.lower() == "no":
                return False
            # If "edit", we could potentially regenerate or let user type extra instructions
            print("Type 'yes' or 'no'. (In V2.1 'edit' will support direct plan revision)")

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
{self.resume_text[:2000]}

ACCESSIBILITY TREE:
{accessibility_tree}

OBSERVE THE SCREENSHOT AND DECIDE THE NEXT STEP.
AVAILABLE ACTIONS:
- CLICK(selector)
- TYPE(selector, text)
- NAVIGATION(url)
- ASK_USER("summary") (Escalate for human help)
- COMPLETE()

SAFETY & STRATEGY:
1. USE ASK_USER IF YOU ARE UNSURE ABOUT A FIELD OR LOGIC.
2. HIGHLIGHT THE RESILIENT RAP FRAMEWORK FOR PhD-RELATED QUESTIONS.
3. NEVER CLICK "SUBMIT" OR "FINISH". INSTEAD, USE ASK_USER("Ready for final review").
4. ALWAYS BE CONCISE IN FORM FIELDS.

NEXT ACTION:
"""
