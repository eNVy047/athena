from enum import Enum
from typing import List

class PluginPermission(Enum):
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    CLIPBOARD = "clipboard"
    BROWSER = "browser"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    TERMINAL = "terminal"
    NOTIFICATIONS = "notifications"
    MEMORY = "memory"
    AUTOMATION = "automation"

class PermissionManager:
    """Manages and checks permissions granted to a plugin."""
    def __init__(self, granted_permissions: List[PluginPermission]):
        self.granted = set(granted_permissions)

    def has_permission(self, permission: PluginPermission) -> bool:
        return permission in self.granted
