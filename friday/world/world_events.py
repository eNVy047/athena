from typing import Dict, Any

class WorldEvent:
    DEVICE_ADDED = "world.device_added"
    DEVICE_REMOVED = "world.device_removed"
    PROJECT_CREATED = "world.project_created"
    PROJECT_UPDATED = "world.project_updated"
    PROJECT_DELETED = "world.project_deleted"
    LOCATION_CHANGED = "world.location_changed"
    APPLICATION_OPENED = "world.application_opened"
    APPLICATION_CLOSED = "world.application_closed"
    USB_CONNECTED = "world.usb_connected"
    USB_DISCONNECTED = "world.usb_disconnected"
    REPOSITORY_CHANGED = "world.repository_changed"

class WorldEventPayload:
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data
        }
