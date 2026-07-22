from typing import Dict, Any
from friday.runtime.progress_tracker import ProgressTracker
from friday.runtime.resource_monitor import ResourceMonitor

class HealthMonitor:
    """Consolidates system health telemetry, execution stats, and error rates."""
    def __init__(self, resource_monitor: ResourceMonitor, progress_tracker: ProgressTracker):
        self.resource_monitor = resource_monitor
        self.progress_tracker = progress_tracker
        self._failed_jobs_count = 0

    def record_failure(self) -> None:
        self._failed_jobs_count += 1

    def get_health_status(self) -> Dict[str, Any]:
        resources = self.resource_monitor.get_resource_usage()
        return {
            "status": "healthy",
            "cpu_usage": resources["cpu_percent"],
            "ram_usage": resources["ram_bytes"],
            "failed_jobs_count": self._failed_jobs_count
        }
