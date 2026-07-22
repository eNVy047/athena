import pytest
from friday.apps.browser.browser_manager import BrowserManager

@pytest.mark.asyncio
async def test_browser_manager_lifecycle():
    manager = BrowserManager()
    
    # Verify initial state
    assert manager.get_state().is_open is False
    
    # Initialize session (headless)
    res = await manager.initialize(headless=True)
    assert res.success is True
    
    state = manager.get_state()
    assert state.is_open is True
    
    # Shutdown
    await manager.shutdown()
    assert manager.get_state().is_open is False
