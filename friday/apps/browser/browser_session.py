from typing import Optional
import logging

from playwright.async_api import async_playwright, Browser, Playwright, BrowserContext as PlaywrightContext
from friday.apps.browser.browser_state import BrowserState
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class BrowserSession:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._default_context: Optional[PlaywrightContext] = None
        self.state = BrowserState()

    async def start(self) -> BrowserResult:
        if self._playwright is not None:
            return BrowserResult(success=True, message="Session already active")
        
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self.headless)
            self._default_context = await self._browser.new_context()
            self.state.is_open = True
            return BrowserResult(success=True, message="Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return BrowserResult(success=False, message="Failed to start", error=str(e))

    async def stop(self) -> None:
        if self._default_context:
            await self._default_context.close()
            self._default_context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        self.state.is_open = False
        
    def get_context(self) -> Optional[PlaywrightContext]:
        return self._default_context
