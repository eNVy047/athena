import time
import httpx
from typing import List, Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.calendar.base import CalendarProvider

class GoogleCalendarProvider(CalendarProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="calendar",
            name="google",
            version="1.0.0",
            capabilities=["get_events", "create_event"]
        )
        super().__init__(metadata, config)
        self.access_token = config.get("GOOGLE_CALENDAR_TOKEN", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.access_token)

    async def get_events(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        start_t = time.time()
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"timeMin": start_time, "timeMax": end_time}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                res_json = response.json()
                
                events = []
                for item in res_json.get("items", []):
                    events.append({
                        "id": item.get("id"),
                        "summary": item.get("summary"),
                        "start": item.get("start", {}).get("dateTime"),
                        "end": item.get("end", {}).get("dateTime")
                    })
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
                return events
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e

    async def create_event(self, details: Dict[str, Any]) -> Dict[str, Any]:
        start_t = time.time()
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=details)
                response.raise_for_status()
                res_json = response.json()
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
                return res_json
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e
