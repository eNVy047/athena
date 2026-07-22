from __future__ import annotations

import os
import shutil
from typing import Any, Dict

class FilesystemActions:
    def __init__(self, platform_adapter: Any):
        self.adapter = platform_adapter

    def execute(self, command: str, arguments: Dict[str, Any]) -> Any:
        path = arguments.get("path", "")
        
        if command == "create":
            content = arguments.get("content", "")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Created file at {path}"
            
        elif command == "delete":
            if os.path.isdir(path):
                shutil.rmtree(path)
                return f"Deleted directory at {path}"
            elif os.path.exists(path):
                os.remove(path)
                return f"Deleted file at {path}"
            return f"Path {path} does not exist"
            
        elif command == "read":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
                
        elif command == "write":
            content = arguments.get("content", "")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Wrote content to {path}"
            
        elif command == "rename":
            new_path = arguments.get("new_path", "")
            shutil.move(path, new_path)
            return f"Renamed {path} to {new_path}"
            
        else:
            raise ValueError(f"Unknown filesystem command: {command}")
