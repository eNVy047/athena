import asyncio
from typing import Set, Any

class ResourceManager:
    def __init__(self):
        self._resources: Set[Any] = set()

    def register(self, resource: Any):
        self._resources.add(resource)

    def unregister(self, resource: Any):
        self._resources.discard(resource)

    async def shutdown(self):
        for resource in list(self._resources):
            try:
                if hasattr(resource, "close"):
                    if asyncio.iscoroutinefunction(resource.close):
                        await resource.close()
                    else:
                        resource.close()
            except Exception:
                pass
        self._resources.clear()
