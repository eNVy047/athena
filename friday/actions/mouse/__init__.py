from __future__ import annotations

from typing import Any, Dict
from friday.actions.platform import PlatformAdapter

class MouseActions:
    def __init__(self, platform_adapter: PlatformAdapter):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        x = int(arguments.get("x", 0))
        y = int(arguments.get("y", 0))
        
        if command == "move":
            self.adapter.mouse_move(x, y)
            return f"Moved mouse to ({x}, {y})"
        elif command == "click":
            self.adapter.mouse_click(x, y)
            return f"Clicked mouse at ({x}, {y})"
        elif command == "double_click":
            self.adapter.mouse_double_click(x, y)
            return f"Double clicked mouse at ({x}, {y})"
        elif command == "right_click":
            self.adapter.mouse_right_click(x, y)
            return f"Right clicked mouse at ({x}, {y})"
        else:
            raise ValueError(f"Unknown mouse command: {command}")
