import pytest
import asyncio
from friday.observability.health_manager import HealthManager
from friday.observability.health import HealthStatus, HealthCheckResult

@pytest.mark.asyncio
async def test_health_manager():
    hm = HealthManager()
    
    async def mock_healthy():
        return HealthCheckResult(component="Mock", status=HealthStatus.READY)
        
    async def mock_failed():
        raise Exception("Database down")
        
    hm.register_checker("DB", mock_failed)
    hm.register_checker("Cache", mock_healthy)
    
    healths = await hm.get_system_health()
    assert healths["DB"].status == HealthStatus.FAILED
    assert healths["Cache"].status == HealthStatus.READY
    
    assert await hm.is_ready() is False
