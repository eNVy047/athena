from dataclasses import dataclass
from typing import Optional, Dict, Any
from friday.events.event_types import Event

PLUGIN_LOADED = "plugin.loaded"
PLUGIN_UNLOADED = "plugin.unloaded"
PLUGIN_ENABLED = "plugin.enabled"
PLUGIN_DISABLED = "plugin.disabled"
PLUGIN_ERROR = "plugin.error"
PLUGIN_PERMISSION_REQUESTED = "plugin.permission_requested"

@dataclass
class PluginEvent(Event):
    plugin_id: str = ""
    plugin_name: str = ""
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PluginStateChangeEvent(PluginEvent):
    old_state: str = ""
    new_state: str = ""
