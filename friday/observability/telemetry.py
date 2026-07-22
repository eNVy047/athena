from friday.observability.metrics import metrics

class TelemetryPublisher:
    """Pushes metrics to external endpoints if configured."""
    
    def __init__(self, endpoint_url: str = ""):
        self.endpoint_url = endpoint_url
        
    async def publish(self) -> bool:
        if not self.endpoint_url:
            return False
            
        metrics.get_summary()
        # In a real system, use httpx to POST data to endpoint_url
        # For now we just return True
        return True
