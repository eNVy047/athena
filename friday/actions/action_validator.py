from __future__ import annotations

from friday.actions.action_models import ActionRequest, ActionType

class ActionValidator:
    def validate(self, request: ActionRequest) -> bool:
        """Validates action parameters before execution."""
        args = request.arguments
        
        if request.action_type == ActionType.MOUSE:
            if request.command in ["move", "click", "double_click", "right_click", "drag"]:
                # Coordinates must be positive numbers
                x = args.get("x", 0)
                y = args.get("y", 0)
                if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                    raise ValueError("Coordinates x and y must be numbers.")
                if x < 0 or y < 0:
                    raise ValueError("Coordinates x and y must be non-negative.")
                    
        elif request.action_type == ActionType.FILESYSTEM:
            path = args.get("path") or args.get("source") or args.get("target") or args.get("filename")
            if not path:
                raise ValueError("Path argument is required for filesystem actions.")
            # Basic path traversal validation
            if ".." in str(path) and not str(path).startswith("/Users/narayanverma/Documents/jarvis/friday"):
                raise ValueError("Directory traversal outside workspace is forbidden.")
                
        elif request.action_type == ActionType.BROWSER:
            if request.command in ["open", "navigate"]:
                url = args.get("url")
                if not url:
                    raise ValueError("URL is required.")
                if not url.startswith(("http://", "https://", "file://", "about:")):
                    raise ValueError("Invalid URL scheme/protocol.")
                    
        return True
