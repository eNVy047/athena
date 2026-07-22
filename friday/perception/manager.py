import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from friday.core.kernel.kernel import FridayKernel
from friday.events.event_bus import EventBus
from friday.perception.sensor import Sensor
from friday.perception.sensor_registry import SensorRegistry
from friday.perception.sensor_loader import SensorLoader
from friday.perception.sensor_context import SensorContext
from friday.perception.perception_pipeline import PerceptionPipeline
from friday.perception.sensor_health import SensorHealth
from friday.perception.sensor_metadata import SensorStatus
from friday.perception.sensor_events import SensorEvent

logger = logging.getLogger(__name__)

class PerceptionManager:
    def __init__(self, kernel: FridayKernel, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        self.kernel = kernel
        self.event_bus = event_bus
        self.config = config or {}

        # Core components
        self.registry = SensorRegistry()
        self.pipeline = PerceptionPipeline(self.event_bus)
        self.health_records: Dict[str, SensorHealth] = {}

        # Background loops
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False

        # Load enabled sensors dynamically
        SensorLoader.load_enabled_sensors(self.registry, self.config)

        # Register health records for each registered sensor
        for sensor in self.registry.list_all():
            self.health_records[sensor.metadata.name] = SensorHealth(sensor.metadata.name)

        # Register inside Friday Kernel and DI
        if hasattr(self.kernel, "services"):
            self.kernel.services.register(PerceptionManager, self)
        if hasattr(self.kernel, "registry"):
            if hasattr(self.kernel.registry, "register"):
                self.kernel.registry.register(PerceptionManager, self)
            elif hasattr(self.kernel.registry, "register_service"):
                self.kernel.registry.register_service("PerceptionManager", self)

        try:
            from friday.core.di import container
            container.register(PerceptionManager, self)
        except Exception:
            pass

    async def start(self) -> None:
        if self.is_running:
            return
        
        logger.info("Starting Perception Subsystem...")
        self.is_running = True
        context = SensorContext(self.event_bus, self.config)

        for sensor in self.registry.list_all():
            try:
                await sensor.initialize(context)
                await sensor.start()
                
                # Start background polling loop for this sensor
                task = asyncio.create_task(self._poll_sensor_loop(sensor))
                self._running_tasks[sensor.metadata.name] = task
                
                health = self.health_records.get(sensor.metadata.name)
                if health:
                    health.record_restart()
                
                await self.event_bus.publish(SensorEvent.SENSOR_STARTED, {"sensor": sensor.metadata.name})
            except Exception as e:
                logger.error(f"Failed to start sensor {sensor.metadata.name}: {e}")
                if sensor.metadata.name in self.health_records:
                    self.health_records[sensor.metadata.name].record_error()

    async def stop(self) -> None:
        if not self.is_running:
            return

        logger.info("Stopping Perception Subsystem...")
        self.is_running = False

        # Cancel polling tasks
        for name, task in list(self._running_tasks.items()):
            task.cancel()
            del self._running_tasks[name]

        # Stop sensors
        for sensor in self.registry.list_all():
            try:
                await sensor.stop()
                await self.event_bus.publish(SensorEvent.SENSOR_STOPPED, {"sensor": sensor.metadata.name})
            except Exception as e:
                logger.error(f"Failed to stop sensor {sensor.metadata.name}: {e}")

    async def pause(self) -> None:
        for sensor in self.registry.list_all():
            if sensor.status == SensorStatus.RUNNING:
                await sensor.pause()
                await self.event_bus.publish(SensorEvent.SENSOR_PAUSED, {"sensor": sensor.metadata.name})

    async def resume(self) -> None:
        for sensor in self.registry.list_all():
            if sensor.status == SensorStatus.PAUSED:
                await sensor.resume()
                await self.event_bus.publish(SensorEvent.SENSOR_RESUMED, {"sensor": sensor.metadata.name})

    async def _poll_sensor_loop(self, sensor: Sensor) -> None:
        sensor_name = sensor.metadata.name
        health = self.health_records[sensor_name]
        
        while self.is_running:
            if sensor.status != SensorStatus.RUNNING:
                await asyncio.sleep(0.5)
                continue

            start_time = time.time()
            try:
                # Observe
                result = await sensor.observe()
                latency = (time.time() - start_time) * 1000.0
                
                if result.success:
                    # Send to pipeline
                    await self.pipeline.process_sensor_reading(sensor_name, result.data)
                    health.record_heartbeat(latency)
                else:
                    health.record_drop()
                    logger.debug(f"Sensor {sensor_name} observation unsuccessful: {result.error}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sensor polling loop for {sensor_name}: {e}")
                health.record_error()
                await self.event_bus.publish(SensorEvent.SENSOR_HEALTH_ALERT, {"sensor": sensor_name, "error": str(e)})

            # Read configuration interval or default to 1 second
            poll_interval = float(self.config.get(f"{sensor_name.upper()}_CAPTURE_INTERVAL", 1.0))
            await asyncio.sleep(poll_interval)

    def get_health_status(self) -> Dict[str, Any]:
        return {name: record.to_dict() for name, record in self.health_records.items()}
