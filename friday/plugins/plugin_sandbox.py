from functools import wraps
from typing import Callable
from friday.plugins.plugin_permissions import PluginPermission

class SecurityException(Exception):
    pass

class PluginSandbox:
    """Enforces execution boundaries for plugins."""
    
    @staticmethod
    def require_permission(perm: PluginPermission):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(self_obj, *args, **kwargs):
                # We expect the plugin class using this to have self.api with has_permission
                if not hasattr(self_obj, 'api') or not self_obj.api.has_permission(perm):
                    raise SecurityException(f"Plugin lacks {perm.value} permission.")
                return await func(self_obj, *args, **kwargs)
            return wrapper
        return decorator
