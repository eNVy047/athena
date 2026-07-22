from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

@dataclass
class Event:
    """Base Friday OS event data structure."""
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

# Predefined Event Types
SYSTEM_STARTUP = "system.startup"
SYSTEM_SHUTDOWN = "system.shutdown"
TELEMETRY_CPU = "telemetry.cpu"
TELEMETRY_BATTERY = "telemetry.battery"
FILESYSTEM_CHANGE = "filesystem.change"
CLIPBOARD_UPDATE = "clipboard.update"
VOICE_INPUT_RECEIVED = "voice.input_received"
ACTION_COMPLETED = "action.completed"
