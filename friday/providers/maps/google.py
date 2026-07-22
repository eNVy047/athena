import time
import httpx
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.maps.base import MapsProvider

class GoogleMapsProvider(MapsProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="maps",
            name="google",
            version="1.0.0",
            capabilities=["get_directions"]
        )
        super().__init__(metadata, config)
        self.api_key = config.get("GOOGLE_MAPS_KEY", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.api_key:
            raise ValueError("Google Maps API Key is required but missing.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def get_directions(self, origin: str, destination: str) -> Dict[str, Any]:
        start_t = time.time()
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                res_json = response.json()
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
                return res_json
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e
