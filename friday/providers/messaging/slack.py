import time
import httpx
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.messaging.base import MessagingProvider

class SlackMessagingProvider(MessagingProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="messaging",
            name="slack",
            version="1.0.0",
            capabilities=["send_message"]
        )
        super().__init__(metadata, config)
        self.bot_token = config.get("SLACK_BOT_TOKEN", "")
        self.timeout = config.get("PROVIDER_TIMEOUT", 30.0)

    async def initialize(self) -> None:
        if not self.bot_token:
            raise ValueError("Slack Bot Token is required.")

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return bool(self.bot_token)

    async def send_message(self, chat_id: str, text: str) -> None:
        start_t = time.time()
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {
            "channel": chat_id,
            "text": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                res_json = response.json()
                if not res_json.get("ok"):
                    raise RuntimeError(f"Slack API error: {res_json.get('error')}")
                self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            raise e
