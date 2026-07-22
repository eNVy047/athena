from typing import Dict
from playwright.async_api import Page
from friday.apps.browser.automation.click_engine import ClickEngine
from friday.apps.browser.automation.typing_engine import TypingEngine
from friday.apps.browser.browser_models import BrowserResult

class FormEngine:
    def __init__(self, page: Page):
        self.page = page
        self.click_engine = ClickEngine(page)
        self.typing_engine = TypingEngine(page)
        
    async def fill_form(self, data: Dict[str, str], submit_selector: str = "") -> BrowserResult:
        for selector, value in data.items():
            res = await self.typing_engine.type_text(selector, value)
            if not res.success:
                return res
                
        if submit_selector:
            return await self.click_engine.click(submit_selector)
            
        return BrowserResult(success=True, message="Form filled successfully")
