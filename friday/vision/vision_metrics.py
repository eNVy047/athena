from dataclasses import dataclass
import time

@dataclass
class VisionMetrics:
    """Tracks latency and performance of the vision pipeline stages."""
    session_id: str
    
    # Timestamps
    pipeline_start_time: float = 0.0
    ocr_start_time: float = 0.0
    ocr_end_time: float = 0.0
    scene_start_time: float = 0.0
    scene_end_time: float = 0.0
    pipeline_end_time: float = 0.0
    
    def start_pipeline(self):
        self.pipeline_start_time = time.time()
        
    def record_ocr_start(self):
        self.ocr_start_time = time.time()
        
    def record_ocr_end(self):
        self.ocr_end_time = time.time()
        
    def record_scene_start(self):
        self.scene_start_time = time.time()
        
    def record_scene_end(self):
        self.scene_end_time = time.time()
        
    def end_pipeline(self):
        self.pipeline_end_time = time.time()

    @property
    def total_duration_ms(self) -> float:
        if self.pipeline_end_time and self.pipeline_start_time:
            return (self.pipeline_end_time - self.pipeline_start_time) * 1000
        return 0.0
