import pytest
from friday.kernel.service_registry import ServiceRegistry

def test_service_registry():
    registry = ServiceRegistry()
    
    class MockService:
        pass
        
    service = MockService()
    registry.register_service("mock", service)
    
    assert registry.get_service("mock") == service
    registry.remove_service("mock")
    assert registry.get_service("mock") is None
