from __future__ import annotations

import logging
import subprocess
import sys
from typing import Any, Dict

logger = logging.getLogger("friday-agent")

class ApplicationActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        app_name = arguments.get("app_name", "")
        
        if command == "launch":
            if sys.platform == "darwin":
                subprocess.run(["open", "-a", app_name])
            elif sys.platform == "win32":
                subprocess.run(["start", app_name], shell=True)
            else:
                subprocess.run([app_name])
            return f"Launched application: {app_name}"
            
        elif command in ["close", "focus"]:
            logger.info(f"[ApplicationAction] {command} app: '{app_name}'")
            return f"Application {command} command executed."
        else:
            raise ValueError(f"Unknown application command: {command}")
