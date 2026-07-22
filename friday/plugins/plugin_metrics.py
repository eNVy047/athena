from dataclasses import dataclass
import time

@dataclass
class PluginMetrics:
    plugin_id: str
    
    start_time: float = 0.0
    end_time: float = 0.0
    
    def start(self):
        self.start_time = time.time()
        
    def end(self):
        self.end_time = time.time()
        
    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
