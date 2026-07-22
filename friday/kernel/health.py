from typing import Dict, Any
from friday.kernel.runtime_state import RuntimeState

class RuntimeHealthMonitor:
    def __init__(self, state: RuntimeState):
        self.state = state

    def check_health(self) -> Dict[str, Any]:
        """Telemetry check for active threads, error logs, and state loads."""
        status = "healthy"
        issues = []
        
        if self.state.background_task_count > 50:
            status = "degraded"
            issues.append("High background task queue size threshold exceeded.")
            
        return {
            "status": status,
            "issues": issues,
            "active_tasks": self.state.background_task_count,
            "browser_sessions": len(self.state.active_browser_tabs)
        }
