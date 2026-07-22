from typing import List

class PermissionGuard:
    def __init__(self, allowed_permissions: List[str]):
        self.allowed_permissions = set(allowed_permissions)

    def is_authorized(self, tool_permissions: List[str]) -> bool:
        """Checks if the active context is authorized to run a tool with these permissions."""
        for perm in tool_permissions:
            if perm not in self.allowed_permissions:
                return False
        return True
