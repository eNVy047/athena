from playwright.async_api import Page
import logging
from friday.apps.browser.browser_models import BrowserResult

logger = logging.getLogger(__name__)

class DOMSnapshotManager:
    """Manages taking full page snapshots and extracting raw HTML/Accessibility trees."""
    
    async def capture_html(self, page: Page) -> BrowserResult:
        try:
            html = await page.content()
            return BrowserResult(success=True, message="HTML captured", data={"html": html})
        except Exception as e:
            logger.error(f"Failed to capture HTML: {e}")
            return BrowserResult(success=False, message="Failed to capture HTML", error=str(e))

    async def capture_accessibility_tree(self, page: Page) -> BrowserResult:
        try:
            tree = await page.accessibility.snapshot()
            return BrowserResult(success=True, message="A11y tree captured", data={"tree": tree})
        except Exception as e:
            logger.error(f"Failed to capture A11y tree: {e}")
            return BrowserResult(success=False, message="Failed to capture A11y tree", error=str(e))
