import logging
from typing import Optional
from friday.apps.browser.browser_session import BrowserSession
from friday.apps.browser.browser_context import BrowserContextManager
from friday.apps.browser.browser_models import BrowserResult
from friday.apps.browser.browser_state import BrowserState

logger = logging.getLogger(__name__)

class BrowserManager:
    """Coordinates Browser Copilot sessions."""
    
    def __init__(self):
        self.session: Optional[BrowserSession] = None
        self.context_manager: Optional[BrowserContextManager] = None
        
    async def initialize(self, headless: bool = False) -> BrowserResult:
        self.session = BrowserSession(headless=headless)
        res = await self.session.start()
        if res.success:
            context = self.session.get_context()
            if context:
                self.context_manager = BrowserContextManager(context)
        return res

    async def shutdown(self):
        if self.session:
            await self.session.stop()
            self.session = None
            self.context_manager = None
            
    def get_state(self) -> BrowserState:
        if self.session:
            return self.session.state
        return BrowserState()
