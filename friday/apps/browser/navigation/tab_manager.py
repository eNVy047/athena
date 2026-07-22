from typing import List
from playwright.async_api import BrowserContext, Page
from friday.apps.browser.browser_models import BrowserResult

class TabManager:
    """Manages multiple tabs within a context."""
    
    def __init__(self, context: BrowserContext):
        self.context = context
        
    def get_tabs(self) -> List[Page]:
        return self.context.pages
        
    async def new_tab(self) -> BrowserResult:
        try:
            await self.context.new_page()
            return BrowserResult(success=True, message="New tab created", data={"page_index": len(self.context.pages)-1})
        except Exception as e:
            return BrowserResult(success=False, message="Failed to create tab", error=str(e))
            
    async def close_tab(self, index: int) -> BrowserResult:
        pages = self.context.pages
        if index < 0 or index >= len(pages):
            return BrowserResult(success=False, message="Invalid tab index")
        
        try:
            await pages[index].close()
            return BrowserResult(success=True, message="Tab closed")
        except Exception as e:
            return BrowserResult(success=False, message="Failed to close tab", error=str(e))
