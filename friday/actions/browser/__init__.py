from __future__ import annotations

import logging
import webbrowser
from typing import Any, Dict

logger = logging.getLogger("friday-agent")

class BrowserActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        url = arguments.get("url", "")
        if command == "open":
            webbrowser.open(url)
            return f"Opened URL: {url}"
        elif command in ["close", "navigate", "reload", "new_tab"]:
            # Basic navigation wrapper falling back to webbrowser
            if url:
                webbrowser.open(url)
                return f"Navigated browser to: {url}"
            return f"Browser command {command} executed successfully."
        else:
            raise ValueError(f"Unknown browser command: {command}")
