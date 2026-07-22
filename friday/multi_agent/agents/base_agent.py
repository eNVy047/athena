import logging
from friday.multi_agent.agent_profile import AgentProfile
from friday.multi_agent.communication.message_bus import MessageBus, AgentMessage

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_id: str, name: str, description: str, message_bus: MessageBus):
        self.profile = AgentProfile(agent_id=agent_id, name=name, description=description)
        self.message_bus = message_bus
        self.message_bus.subscribe(agent_id, self.handle_message)
        
    async def handle_message(self, message: AgentMessage) -> None:
        logger.info(f"{self.profile.name} received message: {message.content}")
        await self.process(message)
        
    async def process(self, message: AgentMessage) -> None:
        raise NotImplementedError
