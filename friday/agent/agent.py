from __future__ import annotations

import logging
from typing import Any, Optional
from friday.agent.agent_session import AgentSession
from friday.agent.request_context import RequestContext
from friday.agent.agent_pipeline import AgentPipeline
from friday.agent.agent_result import AgentResult
from friday.agent.agent_state import AgentStatus
from friday.agent.agent_metrics import AgentMetrics
from friday.agent.agent_hooks import AgentHooks
from friday.agent.conversation_manager import ConversationManager

logger = logging.getLogger("friday-agent")

class Agent:
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
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        self.hooks = AgentHooks()
        self.conversations = ConversationManager()
        
        self.pipeline = AgentPipeline(
            security_manager,
            event_bus,
            memory_manager,
            world_model,
            perception_system,
            cognition_system,
            automation_manager,
            action_manager
        )

    async def handle_request(self, session: AgentSession, request: RequestContext) -> AgentResult:
        """Handles inbound request by setting agent state, executing hooks, and running pipeline."""
        self.status = AgentStatus.PROCESSING
        await self.hooks.run_pre_hooks(request)
        
        # Save query to conversation history
        query = request.payload.get("query", "")
        self.conversations.add_message(session.conversation_id, "user", query)

        result = await self.pipeline.execute(session, request)

        # Record output response
        if result.success:
            self.conversations.add_message(session.conversation_id, "assistant", str(result.output))
        
        self.metrics.record_run(result.success, result.execution_time_ms)
        await self.hooks.run_post_hooks(request, result)
        
        self.status = AgentStatus.IDLE
        return result
