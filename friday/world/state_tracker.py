from typing import Set, Optional, Dict, Any

class StateTracker:
    def __init__(self):
        self.current_activity: Optional[str] = None
        self.current_project: Optional[str] = None
        self.current_application: Optional[str] = None
        self.focused_window: Optional[str] = None
        self.current_location: Optional[str] = None
        self.connected_devices: Set[str] = set()
        self.running_services: Set[str] = set()

    def set_activity(self, activity: str) -> None:
        self.current_activity = activity

    def set_project(self, project_id: str) -> None:
        self.current_project = project_id

    def set_application(self, app_name: str, window_title: Optional[str] = None) -> None:
        self.current_application = app_name
        self.focused_window = window_title

    def set_location(self, location_id: str) -> None:
        self.current_location = location_id

    def add_device(self, device_id: str) -> None:
        self.connected_devices.add(device_id)

    def remove_device(self, device_id: str) -> None:
        self.connected_devices.discard(device_id)

    def start_service(self, service_name: str) -> None:
        self.running_services.add(service_name)

    def stop_service(self, service_name: str) -> None:
        self.running_services.discard(service_name)

    def get_state(self) -> Dict[str, Any]:
        return {
            "current_activity": self.current_activity,
            "current_project": self.current_project,
            "current_application": self.current_application,
            "focused_window": self.focused_window,
            "current_location": self.current_location,
            "connected_devices": list(self.connected_devices),
            "running_services": list(self.running_services)
        }
