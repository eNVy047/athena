import time
from typing import Dict, Optional, Any
from friday.memory.memory_models import MemoryContext


class MemoryCache:
    def __init__(self, enabled: bool = True, ttl: float = 60.0):
        self.enabled = enabled
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, query: str) -> Optional[MemoryContext]:
        if not self.enabled:
            return None

        cached = self._cache.get(query)
        if cached:
            if time.time() - cached["timestamp"] < self.ttl:
                return cached["context"]
            else:
                # Expired
                self._cache.pop(query, None)
        return None

    def set(self, query: str, context: MemoryContext) -> None:
        if not self.enabled:
            return
        self._cache[query] = {"context": context, "timestamp": time.time()}

    def invalidate(self) -> None:
        self._cache.clear()
