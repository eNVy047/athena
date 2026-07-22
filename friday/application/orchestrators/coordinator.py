from typing import Dict, Any, List
from friday.domain.agent import Agent, Plan
from friday.domain.context import ExecutionContext

class AgentCoordinator:
    def __init__(self, agents: List[Agent]):
        self._agents: Dict[str, Agent] = {agent.id: agent for agent in agents}

    def register_agent(self, agent: Agent):
        self._agents[agent.id] = agent

    async def execute_task_with_agent(
        self,
        agent_id: str,
        task_description: str,
        context: ExecutionContext
    ) -> Any:
        """Routes a task execution request to a registered agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} is not registered in the coordinator.")
            
        return await agent.execute(task_description, context)

    def list_agent_capabilities(self) -> Dict[str, List[str]]:
        """Gathers capabilities across all active registered agents."""
        return {aid: agent.capabilities for aid, agent in self._agents.items()}
