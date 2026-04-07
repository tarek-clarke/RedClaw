import asyncio
import json
from typing import List, Dict, Any
from core.browser import BrowserManager
from core.llm import LLMManager
from core.preflight import PreflightManager

class JobDiscovery:
    """Proactively searches for jobs matching the user's profile."""
    
    def __init__(self, browser: BrowserManager, llm: LLMManager, preflight: PreflightManager):
        self.browser = browser
        self.llm = llm
        self.preflight = preflight

    async def generate_search_queries(self) -> List[str]:
        """Generate high-value search keywords from the profile."""
        prompt = f"""
        Based on this User Profile and Resume, generate 5 specific job search queries 
        a professional would use on Google Jobs or LinkedIn.
        Focus on: Specific Tech Stack (AMD, ROCm, Playwright), Seniority, and Domain (ML, PhD, Browser Agents).
        
        PROFILE:
        {json.dumps(self.preflight.profile_data, indent=2)}
        
        RESUME:
        {self.preflight.resume_text[:1000]}
        
        OUTPUT ONLY A JSON LIST OF STRINGS.
        """
        print(f"[REDCLAW] Generating search queries... (Waiting for LM Studio response)")
        messages = [{"role": "user", "content": prompt}]
        try:
            # Short-circuit if model is slow
            response = await asyncio.wait_for(asyncio.to_thread(self.llm.chat_completion, messages), timeout=7.0)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            return json.loads(response)
        except Exception as e:
            print(f"[REDCLAW] LLM Fallback: Using default profile-based queries.")
            return ["Senior Data Engineer Statistics Canada", "PhD ML Engineer ROCm", "Autonomous Analytics Pipeline Developer"]

    async def search_google_jobs(self, query: str) -> List[Dict[str, Any]]:
        """Perform a Google Jobs search and extract results with high resilience."""
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+jobs"
        await self.browser.navigate(search_url)
        
        # Wait for results or human intervention
        await asyncio.sleep(4)
        
        # Broad selectors to catch various Google Job layouts
        results = await self.browser.page.evaluate('''() => {
            const listings = [];
            // Try multiple common Google Job selectors
            const items = document.querySelectorAll('div[data-job-id], .jF57fe, .B8S79c, .G67S8c, .vNEEBe');
            
            items.forEach(item => {
                const titleEl = item.querySelector('.Bj9u3e, .iYjOfc, .P8S79c, h2');
                const companyEl = item.querySelector('.vNEEBe, .v76pQ');
                
                if (titleEl && titleEl.innerText.length > 3) {
                    listings.push({
                        title: titleEl.innerText,
                        company: companyEl ? companyEl.innerText : 'Listed Company',
                        snippet: item.innerText.slice(0, 300),
                        link: window.location.href 
                    });
                }
            });
            return listings;
        }''')
        
        if not results:
            print(f"\n[REDCLAW] WARNING: No job elements detected via DOM selectors.")
            print("[REDCLAW] If the browser is on the correct results page, please click a job or scroll once.")
            print("[REDCLAW] Press 'done' to try extracting again, or 'skip' to move to the next search.")
            while True:
                choice = await asyncio.to_thread(input, "RedClaw Discovery> ")
                if choice.lower() == "done":
                    return await self.search_google_jobs(query)
                if choice.lower() == "skip":
                    return []
            
        return results[:10]

    async def run_discovery(self, goal: str = "Data Engineer") -> List[Dict[str, Any]]:
        """Run the full discovery loop: Query -> Search -> Score -> Rank."""
        print(f"\n[REDCLAW] Launching Discovery Engine V3 (Target: {goal})...")
        
        # 1. Start query generation in background
        query_task = asyncio.create_task(self.generate_search_queries())
        
        # 2. IMMEDIATE ACTION: Start the first search using the user's specific GOAL
        # We add 'jobs' and avoid using the user's name as the primary search
        primary_query = f"{goal} jobs"
        print(f"[REDCLAW] Starting primary search: '{primary_query}'...")
        all_jobs = await self.search_google_jobs(primary_query)
        
        # 3. Now catch up with the LLM-generated queries
        print("[REDCLAW] Checking if LLM has additional high-value queries...")
        try:
            additional_queries = await asyncio.wait_for(query_task, timeout=2.0)
            for q in additional_queries[:1]: # Add one more high-value query
                if q.lower() not in primary_query.lower():
                    print(f"[REDCLAW] Expanding search: '{q}'...")
                    extra_jobs = await self.search_google_jobs(q)
                    all_jobs.extend(extra_jobs)
        except:
            print("[REDCLAW] Primary search complete. (LLM was too slow, skipping expansion)")
        
        if not all_jobs:
            print("[REDCLAW] No jobs found. Try adjusting your goal.")
            return []

        # 4. Scored and ranked jobs
        print(f"\n[REDCLAW] Scoring {len(all_jobs)} jobs for profile fit...")
        # ... (rest of the scoring logic)
        scored_jobs = []
        for job in all_jobs:
            score_data = await self.preflight.get_job_fit_score(job['snippet'])
            job['score'] = score_data.get('score', 0)
            job['recommendation'] = score_data.get('recommendation', 'Review')
            scored_jobs.append(job)
            
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x['score'], reverse=True)
        return scored_jobs
