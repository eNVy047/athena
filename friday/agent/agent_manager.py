from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from friday.agent.agent import Agent

logger = logging.getLogger("friday-agent")

class AgentManager:
    def __init__(
        self,
        security_manager: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
        world_model: Optional[Any] = None,
        perception_system: Optional[Any] = None,
        cognition_system: Optional[Any] = None,
        automation_manager: Optional[Any] = None,
        action_manager: Optional[Any] = None
    ):
        self.dependencies = {
            "security_manager": security_manager,
            "event_bus": event_bus,
            "memory_manager": memory_manager,
            "world_model": world_model,
            "perception_system": perception_system,
            "cognition_system": cognition_system,
            "automation_manager": automation_manager,
            "action_manager": action_manager
        }
        self.agents: Dict[str, Agent] = {}

    def get_or_create_agent(self, agent_id: str) -> Agent:
        if agent_id not in self.agents:
            self.agents[agent_id] = Agent(
                self.dependencies["security_manager"],
                self.dependencies["event_bus"],
                self.dependencies["memory_manager"],
                self.dependencies["world_model"],
                self.dependencies["perception_system"],
                self.dependencies["cognition_system"],
                self.dependencies["automation_manager"],
                self.dependencies["action_manager"]
            )
            logger.info(f"[AgentManager] Initialized agent actor instance: {agent_id}")
        return self.agents[agent_id]

    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"[AgentManager] Removed agent actor: {agent_id}")
