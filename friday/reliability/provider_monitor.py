import logging
from friday.observability.health import HealthStatus, HealthCheckResult

logger = logging.getLogger(__name__)

class ProviderMonitor:
    """Tracks latency and error rates specifically for Providers to support failover."""
    
    def __init__(self):
        self.provider_errors = {}
        
    def record_error(self, provider_id: str):
        self.provider_errors[provider_id] = self.provider_errors.get(provider_id, 0) + 1
        
    def get_health(self, provider_id: str) -> HealthCheckResult:
        errs = self.provider_errors.get(provider_id, 0)
        status = HealthStatus.READY if errs < 5 else HealthStatus.DEGRADED
        if errs > 20:
            status = HealthStatus.FAILED
            
        return HealthCheckResult(
            component=provider_id,
            status=status,
            message=f"{errs} errors recorded" if errs > 0 else "OK"
        )
