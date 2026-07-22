import time
from typing import Dict, Any, Optional
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.storage.base import StorageProvider

class RedisStorageProvider(StorageProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="storage",
            name="redis",
            version="1.0.0",
            capabilities=["get", "set", "delete"]
        )
        super().__init__(metadata, config)
        self.url = config.get("REDIS_URL", "redis://localhost:6379")
        self.client = None

    async def initialize(self) -> None:
        try:
            import redis
            self.client = redis.from_url(self.url, decode_responses=True)
        except ImportError:
            pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False
        self.client = None

    async def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            return bool(self.client.ping())
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        if not self.client:
            raise RuntimeError("Redis client is not installed or initialized.")
        try:
            val = self.client.get(key)
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            return val
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> None:
        start_time = time.time()
        if not self.client:
            raise RuntimeError("Redis client is not installed or initialized.")
        try:
            self.client.set(key, str(value), ex=expire_seconds)
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def delete(self, key: str) -> None:
        start_time = time.time()
        if not self.client:
            raise RuntimeError("Redis client is not installed or initialized.")
        try:
            self.client.delete(key)
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
