from __future__ import annotations

import os
from typing import Any, Dict
from mss import mss

class ScreenActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        if command == "screenshot":
            output_path = arguments.get("output_path", "friday_data/screenshot.png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with mss() as sct:
                sct.shot(output=output_path)
            return f"Screenshot saved to {output_path}"
        else:
            raise ValueError(f"Unknown screen command: {command}")
