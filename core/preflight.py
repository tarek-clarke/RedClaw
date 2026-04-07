import json
from typing import Dict, Any, List, Optional
from core.llm import LLMManager

class PreflightManager:
    """Handles pre-automation logic: Job-fit scoring and common form answers."""
    
    def __init__(self, llm: LLMManager, resume_text: str = "", profile_data: dict = None):
        self.llm = llm
        self.resume_text = resume_text
        self.profile_data = profile_data or {}
        self.common_answers = {
            "work_authorization": "Authorized to work in the US",
            "visa_sponsorship": "No sponsorship required",
            "location": "Remote / New York, NY",
            "willingness_to_relocate": "No",
            "salary_expectations": "Competitive base + equity",
            "notice_period": "2 weeks"
        }

    async def get_job_fit_score(self, job_description: str) -> Dict[str, Any]:
        """Score the job fit using the resume context."""
        prompt = f"""
        Compare this Resume to the Job Description and provide:
        1. A fit score (0-100)
        2. Top 3 matching skills
        3. Top 3 missing signals
        4. Recommendation (Proceed, Review, or Skip)
        
        RESUME:
        {self.resume_text[:2000]}
        
        JOB DESCRIPTION:
        {job_description[:2000]}
        
        JSON OUTPUT:
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.chat_completion(messages)
        try:
            return json.loads(response)
        except:
            return {"score": 0, "recommendation": "Error parsing fit score."}

    def get_common_answer(self, field_name: str) -> Optional[str]:
        """Retrieve a pre-approved answer for common screening questions."""
        # Simple fuzzy match for common answers
        field_name = field_name.lower()
        for key, value in self.common_answers.items():
            if key in field_name:
                return value
        return None

    def add_common_answer(self, key: str, value: str):
        """Allow user to add/update common answers."""
        self.common_answers[key] = value
