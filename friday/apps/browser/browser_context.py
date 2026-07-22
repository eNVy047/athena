from typing import Optional
import logging
from playwright.async_api import BrowserContext as PlaywrightContext, Page
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class BrowserContextManager:
    def __init__(self, context: PlaywrightContext):
        self.context = context
        self.active_page: Optional[Page] = None

    async def new_page(self) -> BrowserResult:
        try:
            self.active_page = await self.context.new_page()
            return BrowserResult(success=True, message="New page created")
        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            return BrowserResult(success=False, message="Failed to create page", error=str(e))
            
    async def get_active_page(self) -> Optional[Page]:
        if not self.active_page:
            pages = self.context.pages
            if pages:
                self.active_page = pages[-1]
        return self.active_page
