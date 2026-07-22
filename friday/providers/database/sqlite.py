import sqlite3
import time
from typing import List, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.database.base import DatabaseProvider

class SqliteDatabaseProvider(DatabaseProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="database",
            name="sqlite",
            version="1.0.0",
            capabilities=["execute_query"]
        )
        super().__init__(metadata, config)
        self.db_path = config.get("SQLITE_DATABASE_DB", "friday_data/database.db")
        self.conn = None

    async def initialize(self) -> None:
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)

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

    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        start_time = time.time()
        params = params or []
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            
            # Fetch details if SELECT
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            else:
                results = [{"rows_affected": cursor.rowcount}]
                
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_time) * 1000)
            return results
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_time) * 1000, error_msg=str(e))
            raise e
