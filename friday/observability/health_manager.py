import time
from typing import Dict, Callable, Awaitable
from friday.observability.health import HealthStatus, HealthCheckResult

class HealthManager:
    """Aggregates health status from Kernel, Providers, Memory, World Model, Automation, Plugins, Voice, Vision, Learning."""
    
    def __init__(self):
        self.checkers: Dict[str, Callable[[], Awaitable[HealthCheckResult]]] = {}

    def register_checker(self, name: str, checker: Callable[[], Awaitable[HealthCheckResult]]):
        self.checkers[name] = checker

    async def get_system_health(self) -> Dict[str, HealthCheckResult]:
        results = {}
        for name, checker in self.checkers.items():
            try:
                start = time.time()
                res = await checker()
                res.latency_ms = (time.time() - start) * 1000
                results[name] = res
            except Exception as e:
                results[name] = HealthCheckResult(
                    component=name, 
                    status=HealthStatus.FAILED, 
                    message=str(e)
                )
        return results

    async def is_ready(self) -> bool:
        healths = await self.get_system_health()
        return all(h.status == HealthStatus.READY for h in healths.values())
