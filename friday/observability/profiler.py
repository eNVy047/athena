import time

class Profiler:
    """Tracks execution time for critical sections."""
    def __init__(self):
        self.sections = {}
        
    def start(self, name: str):
        self.sections[name] = {"start": time.time(), "end": None}
        
    def stop(self, name: str):
        if name in self.sections:
            self.sections[name]["end"] = time.time()
            
    def get_profile(self) -> dict:
        results = {}
        for name, data in self.sections.items():
            if data["start"] and data["end"]:
                results[name] = data["end"] - data["start"]
        return results
