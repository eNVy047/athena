from typing import List
import logging
from friday.multi_agent.agent_registry import AgentRegistry
from friday.multi_agent.communication.message_bus import MessageBus, AgentMessage
from friday.multi_agent.agent_result import AgentResult

logger = logging.getLogger(__name__)

class Coordinator:
    """Central orchestrator for distributed agents."""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        self.registry = registry
        self.message_bus = message_bus
        
    async def delegate(self, objective: str, required_capabilities: List[str]) -> AgentResult:
        logger.info(f"Coordinator evaluating objective: {objective}")
        
        # Find capable agents
        available_agents = []
        for profile in self.registry.get_all_profiles():
            state = self.registry.get_state(profile.agent_id)
            if state and not state.is_busy:
                if any(cap in profile.capabilities for cap in required_capabilities):
                    available_agents.append(profile)
                    
        if not available_agents:
            return AgentResult(success=False, message="No agents available with required capabilities")
            
        # Dispatch to highest priority agent (simplified Dispatcher)
        target = sorted(available_agents, key=lambda a: a.priority, reverse=True)[0]
        logger.info(f"Coordinator dispatching to {target.agent_id}")
        
        # Publish message
        msg = AgentMessage(
            id=f"task_{id(self)}",
            sender_id="coordinator",
            recipient_id=target.agent_id,
            content="execute_task",
            payload={"objective": objective}
        )
        await self.message_bus.publish(msg)
        
        return AgentResult(success=True, message=f"Task delegated to {target.agent_id}")
