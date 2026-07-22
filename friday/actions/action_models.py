from __future__ import annotations

from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    SCREEN = "screen"
    WINDOW = "window"
    FILESYSTEM = "filesystem"
    BROWSER = "browser"
    TERMINAL = "terminal"
    APPLICATION = "application"
    PROCESS = "process"
    CLIPBOARD = "clipboard"
    NOTIFICATION = "notification"
    AUDIO = "audio"
    CAMERA = "camera"
    POWER = "power"
    NETWORK = "network"

class ActionRequest(BaseModel):
    action_type: ActionType
    command: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    timeout: float = 30.0
    retries: int = 0
