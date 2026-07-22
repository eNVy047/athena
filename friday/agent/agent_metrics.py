from __future__ import annotations

from typing import Dict, Any

class AgentMetrics:
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "failed_requests": 0,
            "average_latency_ms": 0.0
        }
        self._total_latency = 0.0

    def record_run(self, success: bool, duration_ms: float) -> None:
        self.metrics["total_requests"] += 1
        if not success:
            self.metrics["failed_requests"] += 1
        self._total_latency += duration_ms
        self.metrics["average_latency_ms"] = self._total_latency / self.metrics["total_requests"]
