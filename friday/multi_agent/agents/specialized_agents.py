import logging
from friday.multi_agent.agents.base_agent import BaseAgent
from friday.multi_agent.communication.message_bus import AgentMessage

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            agent_id="agent_research",
            name="Research Agent",
            description="Searches docs and web for information",
            message_bus=message_bus
        )
        self.profile.capabilities = ["web_search", "document_search"]
        
    async def process(self, message: AgentMessage) -> None:
        logger.info(f"Research Agent processing task: {message.payload.get('objective')}")
        # In full implementation, this uses the F.R.I.D.A.Y. tools
        
class CodingAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(
            agent_id="agent_coding",
            name="Coding Agent",
            description="Writes and refactors code",
            message_bus=message_bus
        )
        self.profile.capabilities = ["code_generation", "code_review"]
        
    async def process(self, message: AgentMessage) -> None:
        logger.info(f"Coding Agent processing task: {message.payload.get('objective')}")
