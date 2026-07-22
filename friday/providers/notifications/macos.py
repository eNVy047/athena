import time
import subprocess
from typing import Dict, Any
from friday.providers.base.provider_metadata import ProviderMetadata
from friday.providers.notifications.base import NotificationsProvider

class MacOsNotificationsProvider(NotificationsProvider):
    def __init__(self, config: Dict[str, Any]):
        metadata = ProviderMetadata(
            category="notifications",
            name="macos",
            version="1.0.0",
            capabilities=["send_notification"]
        )
        super().__init__(metadata, config)

    async def initialize(self) -> None:
        pass

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health_check(self) -> bool:
        return True

    async def send_notification(self, title: str, body: str) -> None:
        start_t = time.time()
        # Clean quotes
        t_clean = title.replace('"', '\\"')
        b_clean = body.replace('"', '\\"')
        cmd = f'display notification "{b_clean}" with title "{t_clean}"'
        try:
            subprocess.run(["osascript", "-e", cmd], capture_output=True, check=True)
            self.health_tracker.record_call(success=True, latency_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            # Fallback for systems/environments without UI capability
            self.health_tracker.record_call(success=False, latency_ms=(time.time() - start_t) * 1000, error_msg=str(e))
            # Don't crash hard if osascript fails, just log it as error
            pass
