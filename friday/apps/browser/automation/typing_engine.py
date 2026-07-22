from playwright.async_api import Page
import logging
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class TypingEngine:
    def __init__(self, page: Page):
        self.page = page
        
    async def type_text(self, selector: str, text: str, delay: int = 0) -> BrowserResult:
        try:
            await self.page.fill(selector, text, timeout=5000)
            return BrowserResult(success=True, message=f"Typed text into {selector}")
        except Exception as e:
            logger.error(f"Typing failed on {selector}: {e}")
            return BrowserResult(success=False, message="Typing failed", error=str(e))
