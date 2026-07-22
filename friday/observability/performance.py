import time

class PerformanceMonitor:
    """Tracks generic performance counters over time."""
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        
    def log_request(self):
        self.request_count += 1
        
    def get_throughput(self) -> float:
        duration = time.time() - self.start_time
        if duration <= 0:
            return 0.0
        return self.request_count / duration
