import json
import os
import time
from datetime import datetime
from typing import Any, Dict

class AuditLogger:
    """Structured JSONL logging for RedClaw actions and human interactions."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.run_id = f"run_{int(time.time())}"
        self.log_path = os.path.join(self.log_dir, f"{self.run_id}.jsonl")

    def log(self, event_type: str, data: Dict[str, Any]):
        """Append a structured event to the log file."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": self.run_id,
            "event_type": event_type,
            **data
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def log_action(self, action_name: str, parameters: Dict[str, Any], status: str = "executed"):
        """Log a browser or agent action."""
        self.log("action", {
            "action": action_name,
            "parameters": parameters,
            "status": status
        })

    def log_approval(self, plan: str, approved: bool, user_input: str = ""):
        """Log a human approval or denial of an action plan."""
        self.log("approval", {
            "plan": plan,
            "approved": approved,
            "user_input": user_input
        })

    def log_error(self, error_msg: str, traceback: str = None):
        """Log an error occurrence."""
        self.log("error", {
            "message": error_msg,
            "traceback": traceback
        })
