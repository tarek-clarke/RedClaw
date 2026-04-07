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
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.chat_completion(messages)
        try:
            return json.loads(response)
        except:
            # Fallback queries
            return ["Senior ML Engineer AMD ROCm", "Autonomous Browser Agent Developer", "PhD Machine Learning Engineer"]

    async def search_google_jobs(self, query: str) -> List[Dict[str, Any]]:
        """Perform a Google Jobs search and extract results."""
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+jobs"
        await self.browser.navigate(search_url)
        # Wait for potential results to load
        await asyncio.sleep(3)
        
        # Extract basic info from the search results
        results = await self.browser.page.evaluate('''() => {
            const listings = [];
            const items = document.querySelectorAll('div[data-job-id], .jF57fe, .B8S79c');
            items.forEach(item => {
                listings.push({
                    title: item.querySelector('.Bj9u3e, .iYjOfc')?.innerText || 'Unknown Title',
                    company: item.querySelector('.vNEEBe, .v76pQ')?.innerText || 'Unknown Company',
                    snippet: item.innerText.slice(0, 200),
                    link: window.location.href // Most links are internal JS clicks in Google Jobs
                });
            });
            return listings.slice(0, 10);
        }''')
        return results

    async def run_discovery(self) -> List[Dict[str, Any]]:
        """Run the full discovery loop: Query -> Search -> Score -> Rank."""
        print("\n[REDCLAW] Generating search queries from your profile...")
        queries = await self.generate_search_queries()
        
        all_jobs = []
        for q in queries[:2]: # Limit to first 2 queries for demo/speed
            print(f"[REDCLAW] Searching for: '{q}'...")
            jobs = await self.search_google_jobs(q)
            all_jobs.extend(jobs)
        
        # Scored and ranked jobs
        scored_jobs = []
        for job in all_jobs:
            score_data = await self.preflight.get_job_fit_score(job['snippet'])
            job['score'] = score_data.get('score', 0)
            job['recommendation'] = score_data.get('recommendation', 'Review')
            scored_jobs.append(job)
            
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x['score'], reverse=True)
        return scored_jobs
