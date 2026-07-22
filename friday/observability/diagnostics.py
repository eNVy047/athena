import sys
import platform
from typing import Dict, Any
from friday.observability.health_manager import HealthManager
from friday.observability.metrics import metrics

class DiagnosticsCollector:
    """Aggregates system info, metrics, and health into a single snapshot."""
    
    def __init__(self, health_manager: HealthManager):
        self.health_manager = health_manager
        
    async def get_diagnostics(self) -> Dict[str, Any]:
        health_data = await self.health_manager.get_system_health()
        return {
            "system": {
                "os": platform.system(),
                "release": platform.release(),
                "python_version": sys.version,
            },
            "metrics": metrics.get_summary(),
            "health": {k: v.status.value for k, v in health_data.items()}
        }
