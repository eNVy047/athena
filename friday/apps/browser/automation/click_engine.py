from playwright.async_api import Page
import logging
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class ClickEngine:
    def __init__(self, page: Page):
        self.page = page
        
    async def click(self, selector: str) -> BrowserResult:
        try:
            await self.page.click(selector, timeout=5000)
            return BrowserResult(success=True, message=f"Clicked {selector}")
        except Exception as e:
            logger.error(f"Click failed on {selector}: {e}")
            return BrowserResult(success=False, message="Click failed", error=str(e))
