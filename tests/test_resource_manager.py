import pytest
from friday.core.resources import ResourceManager

class MockResource:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

@pytest.mark.asyncio
async def test_resource_manager_cleanup():
    mgr = ResourceManager()
    res = MockResource()
    
    mgr.register(res)
    await mgr.shutdown()
    
    assert res.closed
