import asyncio
import os
import json
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
        print(f"[REDCLAW] Planning strategy for goal: {goal}...")
        plan = await asyncio.to_thread(self._generate_action_plan, goal)
        print(f"\n[REDCLAW] PROPOSED ACTION PLAN:\n{plan}")
        
        if not await asyncio.to_thread(self._get_human_approval_sync, plan):
            print("\n[REDCLAW] Plan rejected. Exiting.")
            self.logger.log_approval(str(plan), False, "Terminated by user")
            return

        self.logger.log_approval(str(plan), True)

        while True:
            # 2. Observe
            print("[REDCLAW] Observing screen... (Taking screenshot)")
            screenshot_path = await self.browser.take_screenshot("current_state.png")
            print("[REDCLAW] Analyzing accessibility tree...")
            accessibility_tree = await self.browser.get_accessibility_tree()
            
            # 2.1 CAPTCHA Check (V2.5)
            if self.safety.is_captcha_present(accessibility_tree):
                print(f"\n[REDCLAW] SAFETY TRIGGER: CAPTCHA detected. Pausing for human intervention.")
                await self.browser.wait_for_user()
                continue

            # 3. Decide
            print("[REDCLAW] Consulting AI for next step... (Vision Brain thinking)")
            prompt = self._build_prompt(goal, accessibility_tree)
            response = await asyncio.to_thread(self.llm.multimodal_completion, prompt, screenshot_path)
            
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
                
            # 6. Action Execution (V4.4 Implementation)
            await self._perform_action(response)
            await asyncio.sleep(1) # Small buffer between actions

    def _generate_action_plan(self, goal: str) -> str:
        """Generate a structured plan for the task before execution. (Synchronous for threading)"""
        prompt = f"Generate a high-level step-by-step action plan to achieve this goal: {goal}. Focus on major milestones (e.g., Navigate, Detect Form, Fill, Pause for Submit)."
        messages = [{"role": "user", "content": prompt}]
        return self.llm.chat_completion(messages)

    def _get_human_approval_sync(self, plan: str) -> bool:
        """Request explicit human approval for the proposed plan. (Synchronous for threading)"""
        print("\n[REDCLAW] Do you approve this plan? (yes/no/edit)")
        while True:
            response = input("RedClaw Approve> ")
            if response.lower() == "yes":
                return True
            if response.lower() == "no":
                return False
            print("Type 'yes' or 'no'.")

    async def _perform_action(self, response: str):
        """Parse and execute the action string from the LLM."""
        try:
            if "CLICK(" in response:
                selector = response.split("CLICK(")[1].split(")")[0].strip("'\"")
                print(f"[REDCLAW] Action: Clicking {selector}")
                await self.browser.page.click(selector, timeout=5000)
                
            elif "TYPE(" in response:
                parts = response.split("TYPE(")[1].split(")") [0].split(",")
                selector = parts[0].strip().strip("'\"")
                text = parts[1].strip().strip("'\"")
                print(f"[REDCLAW] Action: Typing into {selector}")
                await self.browser.page.fill(selector, text, timeout=5000)
                
            elif "NAVIGATION(" in response:
                url = response.split("NAVIGATION(")[1].split(")")[0].strip("'\"")
                print(f"[REDCLAW] Action: Navigating to {url}")
                await self.browser.navigate(url)
                
        except Exception as e:
            print(f"[REDCLAW] Action Error: {str(e)}")
            self.logger.log("action_error", {"error": str(e), "action": response})

    def _build_prompt(self, goal: str, accessibility_tree: str) -> str:
        """Construct the prompt for the multi-modal model with the full profile context."""
        
        # Serialize the entire profile for the LLM to use dynamically
        profile_json = json.dumps(self.profile_data, indent=2)

        return f"""
YOU ARE REDCLAW, A UNIVERSAL BROWSER ASSISTANT FOR AMD USERS.
YOUR GOAL: {goal}

USER PROFILE DATA:
{profile_json}

RESUME CONTEXT (FOR JOB TASKS):
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

STRATEGY:
1. MATCH FORM FIELDS ON SCREEN TO VALUES IN THE "USER PROFILE DATA".
2. USE THE "RESUME CONTEXT" ONLY IF THE TASK IS JOB-RELATED OR REQUIRES WORK HISTORY.
3. USE ASK_USER IF A FIELD REQUIRES DATA YOU DO NOT HAVE.
4. FOR CRITICAL BUTTONS (SUBMIT, APPLY, FINISH, BUY, PAY), USE ASK_USER("Ready for final review").
5. ALWAYS BE CONCISE.

NEXT ACTION:
"""
