from __future__ import annotations

import pyperclip
from typing import Any, Dict

class ClipboardActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        if command == "write":
            text = arguments.get("text", "")
            pyperclip.copy(text)
            return "Wrote text to clipboard"
            
        elif command == "read":
            return pyperclip.paste()
            
        elif command == "clear":
            pyperclip.copy("")
            return "Cleared clipboard"
            
        else:
            raise ValueError(f"Unknown clipboard command: {command}")
