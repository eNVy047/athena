import logging
import os
from typing import Dict, Any, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from friday.perception.sensor import Sensor
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

logger = logging.getLogger(__name__)

class FilesystemObservationHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.events = []

    def on_any_event(self, event):
        # Ignore pycache or temp git files to prevent noise
        if ".git" in event.src_path or "__pycache__" in event.src_path or ".pytest_cache" in event.src_path:
            return
        self.events.append({
            "event_type": event.event_type,
            "is_directory": event.is_directory,
            "src_path": event.src_path,
            "dest_path": getattr(event, "dest_path", None)
        })

class FilesystemSensor(Sensor):
    def __init__(self):
        metadata = SensorMetadata(
            name="filesystem",
            description="Observes filesystem modifications using watchdog",
            version="1.0.0",
            capabilities=["filesystem.file_watch"],
            required_permissions=[]
        )
        super().__init__(metadata)
        self.watch_paths = []
        self.observer = None
        self.handler = None

    async def initialize(self, context: SensorContext) -> None:
        await super().initialize(context)
        paths_str = self.context.config.get("FILESYSTEM_WATCH_PATHS", "")
        # Default to watching workspace root if empty
        if not paths_str:
            self.watch_paths = [os.getcwd()]
        else:
            self.watch_paths = [p.strip() for p in paths_str.split(",") if p.strip()]

    async def start(self) -> None:
        await super().start()
        self.handler = FilesystemObservationHandler()
        self.observer = Observer()
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.handler, path, recursive=True)
                logger.info(f"Watchdog scheduling watch on path: {path}")
        self.observer.start()

    async def pause(self) -> None:
        await super().pause()

    async def resume(self) -> None:
        await super().resume()

    async def stop(self) -> None:
        await super().stop()
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.handler = None

    async def health_check(self) -> bool:
        return self.observer is not None and self.observer.is_alive()

    async def observe(self) -> SensorResult:
        if self.status != SensorStatus.RUNNING:
            return SensorResult(success=False, error="Sensor not running")

        if not self.handler:
            return SensorResult(success=False, error="Filesystem handler unavailable")

        # Swap list to collect latest events and clear old ones
        current_events = self.handler.events
        self.handler.events = []
        
        return SensorResult(success=True, data={
            "events": current_events
        })
