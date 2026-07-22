import os
import psutil
from typing import Dict, Any

class ResourceMonitor:
    """Monitors CPU, RAM usage, and active handle diagnostics on the host system."""
    def __init__(self):
        self._process = psutil.Process(os.getpid())

    def get_resource_usage(self) -> Dict[str, Any]:
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_bytes": psutil.virtual_memory().used,
            "process_cpu": self._process.cpu_percent(),
            "process_ram_rss": self._process.memory_info().rss
        }
