from __future__ import annotations

from typing import Any, Dict
from friday.actions.platform import PlatformAdapter

class NotificationActions:
    def __init__(self, platform_adapter: PlatformAdapter):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        title = arguments.get("title", "Friday")
        message = arguments.get("message", "")
        
        if command == "show":
            self.adapter.show_notification(title, message)
            return f"Notification shown: {title} - {message}"
        else:
            raise ValueError(f"Unknown notification command: {command}")
