import pytest
from core.safety_policy import SafetyPolicy

def test_domain_whitelist():
    """Test that only allowed domains pass the safety check."""
    policy = SafetyPolicy()
    assert policy.is_domain_allowed("https://greenhouse.io/jobs") == True
    assert policy.is_domain_allowed("https://lever.co/careers") == True
    assert policy.is_domain_allowed("https://malicious-site.com") == False

def test_action_gating():
    """Test that high-priority actions trigger a pause."""
    policy = SafetyPolicy()
    assert policy.should_pause_before_action("SUBMIT") == True
    assert policy.should_pause_before_action("LOGIN") == True
    assert policy.should_pause_before_action("CLICK", "Click the Submit button") == True
    assert policy.should_pause_before_action("CLICK", "Click the 'Next' button") == False

def test_navigation_validation():
    """Test that navigation to unauthorized domains is blocked."""
    policy = SafetyPolicy()
    assert policy.validate_navigation("https://google.com") is None
    assert "not in the allowed list" in policy.validate_navigation("https://unsafe.com")
