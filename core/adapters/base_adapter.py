from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAdapter(ABC):
    """Base class for all site-specific application adapters."""
    
    @abstractmethod
    def matches(self, url: str) -> bool:
        """Check if this adapter handles the target URL."""
        pass

    @abstractmethod
    def extract_metadata(self, page_text: str) -> Dict[str, Any]:
        """Extract job title, company, and required fields from page text."""
        pass

    @abstractmethod
    def get_field_selectors(self) -> Dict[str, str]:
        """Return common selectors for standard fields (e.g., 'first_name', 'email')."""
        pass

    def map_profile_to_fields(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Map generic profile data to adapter-specific field values."""
        # Default implementation: simple pass-through
        return profile
