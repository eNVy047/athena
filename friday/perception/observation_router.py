import logging
from friday.events.event_bus import EventBus
from friday.perception.observation import Observation

logger = logging.getLogger(__name__)

class ObservationRouter:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def route(self, observation: Observation) -> None:
        event_type = f"perception.observation.{observation.sensor_name}"
        logger.debug(f"Routing observation from {observation.sensor_name} to event {event_type}")
        
        # Publish to EventBus so handlers/skills/WorldModel can react
        await self.event_bus.publish(event_type, observation.to_dict())
        # Publish to general observation stream
        await self.event_bus.publish("perception.observation", observation.to_dict())
