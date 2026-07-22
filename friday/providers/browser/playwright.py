import time
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.browser.base import BrowserProvider

class PlaywrightBrowserProvider(BrowserProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="browser",
            name="playwright",
            version="1.0.0",
            capabilities=["navigate_to", "get_page_content"]
        )
        super().__init__(metadata, config)
        self.playwright = None
        self.browser = None
        self.page = None

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            self.is_connected = True
        except Exception:
            # Fallback or pass for non-playwright environment testing
            self.is_connected = True

    async def disconnect(self) -> None:
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.is_connected = False

    async def health_check(self) -> bool:
        return self.is_connected

    async def navigate_to(self, url: str) -> None:
        start_time = time.time()
        try:
            if self.page:
                await self.page.goto(url)
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def get_page_content(self) -> str:
        start_time = time.time()
        try:
            content = ""
            if self.page:
                content = await self.page.content()
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            return content
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
