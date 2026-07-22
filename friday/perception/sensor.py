from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from friday.perception.sensor_metadata import SensorMetadata, SensorStatus
from friday.perception.sensor_context import SensorContext
from friday.perception.sensor_result import SensorResult

class Sensor(ABC):
    def __init__(self, metadata: SensorMetadata):
        self.metadata = metadata
        self.status = SensorStatus.OFFLINE
        self.context: Optional[SensorContext] = None

    @abstractmethod
    async def initialize(self, context: SensorContext) -> None:
        self.context = context
        self.status = SensorStatus.INITIALIZED

    @abstractmethod
    async def start(self) -> None:
        self.status = SensorStatus.RUNNING

    @abstractmethod
    async def pause(self) -> None:
        self.status = SensorStatus.PAUSED

    @abstractmethod
    async def resume(self) -> None:
        self.status = SensorStatus.RUNNING

    @abstractmethod
    async def stop(self) -> None:
        self.status = SensorStatus.OFFLINE

    @abstractmethod
    async def health_check(self) -> bool:
        return self.status != SensorStatus.ERROR

    @abstractmethod
    async def observe(self) -> SensorResult:
        pass
