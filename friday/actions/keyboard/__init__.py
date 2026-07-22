from __future__ import annotations

from typing import Any, Dict
from friday.actions.platform import PlatformAdapter

class KeyboardActions:
    def __init__(self, platform_adapter: PlatformAdapter):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        if command == "type":
            text = arguments.get("text", "")
            self.adapter.keyboard_type(text)
            return f"Typed text: {text}"
        elif command == "press":
            key = arguments.get("key", "")
            self.adapter.keyboard_press(key)
            return f"Pressed key: {key}"
        elif command == "hotkey":
            keys = arguments.get("keys", [])
            self.adapter.keyboard_hotkey(keys)
            return f"Executed hotkey: {keys}"
        else:
            raise ValueError(f"Unknown keyboard command: {command}")
