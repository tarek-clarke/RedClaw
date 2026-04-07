from typing import Dict, Any, Optional
from core.adapters.base_adapter import BaseAdapter

class GreenhouseAdapter(BaseAdapter):
    """Adapter for Greenhouse.io job boards."""
    
    def matches(self, url: str) -> bool:
        """Check if the URL belongs to Greenhouse."""
        return "greenhouse.io" in url or "boards.greenhouse.io" in url

    def extract_metadata(self, page_text: str) -> Dict[str, Any]:
        """Extract basic Greenhouse job information."""
        # This would use simple heuristics/regex or LLM parsing in a real scenario
        return {
            "platform": "Greenhouse",
            "metadata_fields": ["job_title", "location"]
        }

    def get_field_selectors(self) -> Dict[str, str]:
        """Return common Greenhouse field selectors."""
        return {
            "first_name": "#first_name",
            "last_name": "#last_name",
            "email": "#email",
            "phone": "#phone",
            "resume": "#resume_upload"
        }

    def map_profile_to_fields(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Map generic profile data to Greenhouse values."""
        # Example mapped result
        return {
            "first_name": profile.get("full_name", "").split(" ")[0],
            "last_name": " ".join(profile.get("full_name", "").split(" ")[1:]),
            "email": profile.get("email"),
            "phone": profile.get("phone")
        }
