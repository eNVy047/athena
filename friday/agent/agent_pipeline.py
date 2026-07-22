from __future__ import annotations

import time
import logging
from typing import Any, Optional
from friday.agent.request_context import RequestContext
from friday.agent.agent_session import AgentSession
from friday.agent.agent_context import AgentContext
from friday.agent.agent_permissions import AgentPermissionManager
from friday.agent.agent_validator import AgentValidator
from friday.agent.agent_events import AgentEvents
from friday.agent.agent_result import AgentResult
from friday.agent.agent_router import AgentRouter

logger = logging.getLogger("friday-agent")

class AgentPipeline:
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
        self.permissions = AgentPermissionManager(security_manager)
        self.validator = AgentValidator()
        self.events = AgentEvents(event_bus)
        self.router = AgentRouter()
        
        self.memory = memory_manager
        self.world = world_model
        self.perception = perception_system
        self.cognition = cognition_system
        self.automation = automation_manager
        self.action = action_manager

    async def execute(self, session: AgentSession, request: RequestContext) -> AgentResult:
        """Runs the entire F.R.I.D.A.Y. Agent Pipeline sequentially."""
        start_time = time.time()
        conversation_id = session.conversation_id
        await self.events.publish_started(conversation_id, request.request_id)

        try:
            # 1. Normalize and Validate Request
            payload = request.payload
            self.validator.validate_request(payload)
            query = payload["query"]
            user_id = payload["user_id"]

            # 2. Permission Check
            allowed = await self.permissions.check_request_permissions(user_id, "execute")
            if not allowed:
                err_msg = "Request blocked: insufficient privileges."
                await self.events.publish_completed(conversation_id, success=False, error=err_msg)
                return AgentResult(success=False, error=err_msg)

            # 3. Retrieve Memory
            if self.memory:
                try:
                    await self.memory.sync_turn(query)
                except Exception as e:
                    logger.error(f"[AgentPipeline] Memory sync error: {e}")

            # 4. Read World Model
            world_state = {}
            if self.world:
                world_state = self.world.get_state()

            # 5. Gather Perception Snapshot
            perception_snapshot = {}
            if self.perception:
                perception_snapshot = self.perception.get_snapshot()

            # Create integrated Context
            AgentContext(
                perception_snapshot=perception_snapshot,
                world_state=world_state,
                clipboard=""
            )

            # 6. Route & Decide Execution Paths
            route_info = self.router.route_request(query)
            output = f"Processed request matching route: {route_info['route']}"

            # 7. Execute Route actions/automations
            if route_info["route"] == "automation" and self.automation:
                # Mock workflow execution
                pass
            elif route_info["route"] == "action_layer" and self.action:
                # Mock direct action execution
                pass
            elif self.cognition:
                # Fallback: run cognition LLM plans if available
                pass

            # 8. Store Memory of completed request
            if self.memory:
                await self.memory.store_memory(
                    content=f"User requested: '{query}'. Pipeline executed route: {route_info['route']}.",
                    category="conversation"
                )

            # 9. Return Response
            duration = (time.time() - start_time) * 1000
            await self.events.publish_completed(conversation_id, success=True)
            return AgentResult(
                success=True,
                output=output,
                execution_time_ms=duration
            )

        except Exception as e:
            logger.error(f"[AgentPipeline] Execution failed: {e}", exc_info=True)
            duration = (time.time() - start_time) * 1000
            await self.events.publish_completed(conversation_id, success=False, error=str(e))
            return AgentResult(
                success=False,
                error=str(e),
                execution_time_ms=duration
            )
