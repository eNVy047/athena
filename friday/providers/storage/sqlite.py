import sqlite3
import time
import json
from typing import Dict, Any, Optional
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.storage.base import StorageProvider

class SqliteStorageProvider(StorageProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="storage",
            name="sqlite",
            version="1.0.0",
            capabilities=["get", "set", "delete"]
        )
        super().__init__(metadata, config)
        self.db_path = config.get("SQLITE_STORAGE_DB", "friday_data/storage.db")
        self.conn = None

    async def initialize(self) -> None:
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS key_value (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
        )
        self.conn.commit()

    async def connect(self) -> None:
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
        self.is_connected = True

    async def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
        self.is_connected = False

    async def health_check(self) -> bool:
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0] == 1
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT value, expires_at FROM key_value WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            if not row:
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
                return None
            
            val_str, expires_at = row
            if expires_at and expires_at < time.time():
                cursor.execute("DELETE FROM key_value WHERE key = ?", (key,))
                self.conn.commit()
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
                return None
                
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            return json.loads(val_str)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> None:
        start_time = time.time()
        try:
            val_str = json.dumps(value)
            expires_at = time.time() + expire_seconds if expire_seconds else None
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO key_value (key, value, expires_at) VALUES (?, ?, ?)",
                (key, val_str, expires_at)
            )
            self.conn.commit()
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e

    async def delete(self, key: str) -> None:
        start_time = time.time()
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM key_value WHERE key = ?", (key,))
            self.conn.commit()
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
