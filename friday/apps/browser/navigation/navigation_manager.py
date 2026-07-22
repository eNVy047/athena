import logging
from playwright.async_api import Page
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class NavigationManager:
    """Handles routing, navigation, and history for a specific Page."""
    
    def __init__(self, page: Page):
        self.page = page

    async def goto(self, url: str) -> BrowserResult:
        try:
            if not url.startswith("http"):
                url = "https://" + url
            response = await self.page.goto(url, wait_until="networkidle")
            status = response.status if response else 0
            return BrowserResult(success=True, message=f"Navigated to {url}", data={"status": status})
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            return BrowserResult(success=False, message="Navigation failed", error=str(e))
            
    async def reload(self) -> BrowserResult:
        try:
            await self.page.reload(wait_until="networkidle")
            return BrowserResult(success=True, message="Page reloaded")
        except Exception as e:
            return BrowserResult(success=False, message="Reload failed", error=str(e))
