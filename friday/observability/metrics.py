from typing import Dict
from collections import defaultdict
import threading

class MetricsRegistry:
    """Collects CPU, RAM, GPU, Token usage, Provider latency/failures, Workflow/Action latency, Voice/Vision/Memory latency, Plugin load time."""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.latencies: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def inc(self, metric: str, amount: int = 1):
        with self.lock:
            self.counters[metric] += amount

    def record_latency(self, metric: str, duration_ms: float):
        with self.lock:
            self.latencies[metric].append(duration_ms)

    def get_summary(self) -> Dict[str, dict]:
        with self.lock:
            summary = {}
            for k, v in self.counters.items():
                summary[k] = {"count": v}
            for k, v in self.latencies.items():
                if v:
                    summary[f"{k}_latency"] = {
                        "avg": sum(v) / len(v),
                        "max": max(v),
                        "min": min(v)
                    }
            return summary

metrics = MetricsRegistry()
