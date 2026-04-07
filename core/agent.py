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
        try:
            # V4.9: Agent-level timeout so we never hang forever
            plan = await asyncio.wait_for(asyncio.to_thread(self._generate_action_plan, goal), timeout=15.0)
        except asyncio.TimeoutError:
            print("[REDCLAW] AI Connection slow. Falling back to default 'Direct Form Analysis' strategy.")
            plan = "1. Navigate to page. 2. Identify form fields. 3. Populate fields from profile. 4. Wait for manual review."
        except Exception as e:
            print(f"[REDCLAW] AI Offline ({str(e)}). Using local fallback strategy.")
            plan = "1. Load page. 2. Auto-detect inputs. 3. Fill profile data."
        
        print(f"\n[REDCLAW] PROPOSED ACTION PLAN:\n{plan}")
        
        if not await asyncio.to_thread(self._get_human_approval_sync, plan):
            print("\n[REDCLAW] Plan rejected. Exiting.")
            self.logger.log_approval(str(plan), False, "Terminated by user")
            return

        self.logger.log_approval(str(plan), True)

        while True:
            # 2. Observe (V6.0: Text-only DOM scan, no screenshots needed)
            print("[REDCLAW] Scanning page DOM for form fields...")
            dom_snapshot = await self.browser.get_accessibility_tree()

            # 3. Decide (V6.0: Pure text reasoning — no vision model needed)
            print("[REDCLAW] Consulting AI for next step... (Text Brain thinking)")
            prompt = self._build_prompt(goal, dom_snapshot)
            messages = [{"role": "user", "content": prompt}]
            try:
                response = await asyncio.wait_for(asyncio.to_thread(self.llm.chat_completion, messages), timeout=20.0)
            except asyncio.TimeoutError:
                print("[REDCLAW] AI timed out. Pausing for human help.")
                response = "ASK_USER(\"AI is taking too long. Please assist.\")"
            except Exception as e:
                print(f"[REDCLAW] AI Error: {str(e)}")
                response = "ASK_USER(\"AI encountered an error. Please assist.\")"
            
            print(f"\n[REDCLAW] Agent Decision: {response}")
            self.logger.log("decision", {"response": response})
            
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
        """Generate a structured, browser-level action plan for the current URL. (Synchronous)"""
        url = self.browser.page.url
        prompt = f"""
        GOAL: {goal}
        CURRENT SITE: {url}
        
        Generate a concise, 4-5 step BROWSER EXECUTION PLAN for this specific task.
        DO NOT give career advice or long-term timelines.
        FOCUS ON: 
        1. Form Detection (Which fields are we looking for?)
        2. Data Entry (Mapping user profile to this site)
        3. File Handling (Resume/Portfolio)
        4. Review & Submit (Final human-in-the-loop checkpoint)
        """
        messages = [{"role": "user", "content": prompt}]
        return self.llm.chat_completion(messages)

    def _get_human_approval_sync(self, plan: str) -> bool:
        """Request explicit human approval for the proposed plan. (Synchronous for threading)"""
        print("\n[REDCLAW] Do you approve this browser execution plan? (yes/no)")
        print("[REDCLAW] Type 'no' if the plan is too broad or contains non-browser 'career advice'.")
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

    def _build_prompt(self, goal: str, dom_snapshot: str) -> str:
        """Build a compact text-only prompt that fits in small context windows (V6.1)."""
        # Flatten profile to key=value pairs instead of full JSON
        profile_lines = []
        for key, val in self.profile_data.items():
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    profile_lines.append(f"  {key}.{k2}: {v2}")
            elif isinstance(val, list):
                profile_lines.append(f"  {key}: {', '.join(str(v) for v in val)}")
            else:
                profile_lines.append(f"  {key}: {val}")
        profile_text = "\n".join(profile_lines[:20])  # Cap at 20 fields

        # Truncate DOM to fit context
        dom_trimmed = dom_snapshot[:2000]

        return f"""You are REDCLAW, a browser agent filling a web form.

PROFILE:
{profile_text}

PAGE:
{dom_trimmed}

RULES:
- Output ONE action only. No explanation.
- Use exact selector values from PAGE above.
- Fill the first EMPTY field from the top.
- Skip [FILLED] fields.
- For file uploads: ASK_USER("Please upload resume manually")
- For Submit/Apply buttons: ASK_USER("Ready to submit. Please review.")
- When all fields are filled: COMPLETE()

ACTIONS:
- TYPE("selector", "value")
- CLICK("selector")
- ASK_USER("message")
- COMPLETE()

NEXT ACTION:"""

