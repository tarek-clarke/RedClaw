from typing import List, Optional
from urllib.parse import urlparse
from config import ALLOWED_DOMAINS, PAUSE_BEFORE_SUBMIT, PAUSE_BEFORE_LOGIN, PAUSE_BEFORE_FILE_UPLOAD

class SafetyPolicy:
    """Enforces safety rules for browser navigation and actions."""
    
    def __init__(self):
        self.allowed_domains = ALLOWED_DOMAINS

    def is_domain_allowed(self, url: str) -> bool:
        """Check if the target URL's domain is in the whitelist."""
        try:
            domain = urlparse(url).netloc
            if not domain:
                return True # Local or relative path
            
            return any(domain.endswith(d) for d in self.allowed_domains)
        except Exception:
            return False

    def is_captcha_present(self, text: str) -> bool:
        """Detect CAPTCHA-related keywords in page text."""
        captcha_keywords = ["captcha", "robot", "human", "verify your identity", "solve to continue"]
        return any(kw in text.lower() for kw in captcha_keywords)

    def should_pause_before_action(self, action_type: str, action_data: str = "") -> bool:
        """Determine if a manual pause is required based on action type."""
        action_type = action_type.upper()
        
        if action_type == "SUBMIT" and PAUSE_BEFORE_SUBMIT:
            return True
        if action_type == "LOGIN" and PAUSE_BEFORE_LOGIN:
            return True
        if action_type == "UPLOAD" and PAUSE_BEFORE_FILE_UPLOAD:
            return True
            
        # Check for keywords in general actions
        if any(key in action_data.upper() for key in ["SUBMIT", "APPLY", "FINISH"]):
            return PAUSE_BEFORE_SUBMIT
            
        return False

    def validate_navigation(self, url: str) -> Optional[str]:
        """Verify navigation is safe. Returns an error message if blocked."""
        if not self.is_domain_allowed(url):
            return f"Domain '{urlparse(url).netloc}' is not in the allowed list."
        return None
