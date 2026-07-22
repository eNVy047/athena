import time
from typing import Dict, Any

class ProviderHealthTracker:
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.last_latency_ms = 0.0
        self.total_latency_ms = 0.0
        self.errors: Dict[str, int] = {}
        self.usage_metrics: Dict[str, Any] = {}
        self.cost = 0.0

    def record_call(self, success: bool, latency_ms: float, error_msg: str = None, cost: float = 0.0, **kwargs):
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if error_msg:
                self.errors[error_msg] = self.errors.get(error_msg, 0) + 1
        self.last_latency_ms = latency_ms
        self.total_latency_ms += latency_ms
        self.cost += cost
        for k, v in kwargs.items():
            if isinstance(v, (int, float)):
                self.usage_metrics[k] = self.usage_metrics.get(k, 0) + v

    @property
    def average_latency_ms(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_latency_ms / self.total_calls

    @property
    def availability(self) -> float:
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "availability": self.availability,
            "average_latency_ms": self.average_latency_ms,
            "failed_calls": self.failed_calls,
            "cost": self.cost,
            "usage": self.usage_metrics,
            "errors": self.errors
        }
