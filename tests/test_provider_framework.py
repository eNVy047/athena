import pytest
from typing import Dict, Any, List
from friday.providers.base.provider import Provider
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.base.provider_registry import ProviderRegistry
from friday.providers.base.provider_manager import ProviderManager
from friday.providers.base.provider_config import ProviderConfig

class DummyTestProvider(Provider):
    def __init__(self, name: str, success: bool = True):
        metadata = ProviderMetadata(
            category="test_category",
            name=name,
            version="1.0.0",
            capabilities=["test_op"]
        )
        super().__init__(metadata, {})
        self.success = success
        self.called = False

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return self.success

    async def test_op(self) -> str:
        self.called = True
        if not self.success:
            raise RuntimeError("Operation failed")
        self.health_tracker.record_call(success=True, latency_ms=0.0)
        return f"success_from_{self.metadata.name}"

@pytest.mark.asyncio
async def test_registry_registration_and_fallback_chain():
    registry = ProviderRegistry()
    
    p1 = DummyTestProvider("primary")
    p2 = DummyTestProvider("fallback1")
    p3 = DummyTestProvider("fallback2")
    
    registry.register(p1)
    registry.register(p2)
    registry.register(p3)
    
    registry.set_fallbacks("test_category", ["primary", "fallback1", "fallback2"])
    
    chain = registry.get_fallback_chain("test_category", "primary")
    assert [p.metadata.name for p in chain] == ["primary", "fallback1", "fallback2"]

@pytest.mark.asyncio
async def test_manager_execution_with_fallback_success():
    config = {
        "TEST_CATEGORY_PROVIDER": "primary",
        "PROVIDER_TIMEOUT": 5.0,
        "PROVIDER_RETRY_COUNT": 1
    }
    manager = ProviderManager(config)
    
    # Register mock providers
    p1 = DummyTestProvider("primary", success=False)
    p2 = DummyTestProvider("fallback1", success=True)
    
    manager.registry.register(p1)
    manager.registry.register(p2)
    manager.registry.set_fallbacks("test_category", ["primary", "fallback1"])
    
    async def op(provider: DummyTestProvider):
        return await provider.test_op()
        
    result = await manager.execute_with_fallback("test_category", op)
    
    assert result == "success_from_fallback1"
    assert p1.health_tracker.failed_calls == 1
    assert p2.health_tracker.successful_calls == 1
