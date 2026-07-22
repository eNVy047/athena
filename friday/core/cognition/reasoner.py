import logging
from typing import Dict, Any, List
from friday.core.cognition.models import Goal, Intent, Plan, Decision, Evaluation, Reflection
from friday.core.cognition.intent_engine import IntentEngine
from friday.core.cognition.planner import Planner
from friday.core.cognition.decision_engine import DecisionEngine
from friday.core.cognition.executor import Executor
from friday.core.cognition.critic import Critic
from friday.core.cognition.reflection import ReflectionEngine
from friday.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class Reasoner:
    """The central reasoning engine managing Friday cognitive execution loops."""
    def __init__(
        self,
        event_bus: EventBus,
        intent_engine: IntentEngine,
        planner: Planner,
        decision_engine: DecisionEngine,
        executor: Executor,
        critic: Critic,
        reflection_engine: ReflectionEngine
    ):
        self.event_bus = event_bus
        self.intent_engine = intent_engine
        self.planner = planner
        self.decision_engine = decision_engine
        self.executor = executor
        self.critic = critic
        self.reflection_engine = reflection_engine

    async def reason_and_execute(self, raw_request: str) -> bool:
        logger.info(f"Reasoner starting turn for request: {raw_request}")
        
        # 1. Intent Parsing
        intent = await self.intent_engine.parse(raw_request)
        await self.event_bus.publish("cognition.intent_parsed", {"intent_id": intent.id, "name": intent.name})

        # 2. Plan Generation
        plan = await self.planner.generate_plan(intent.id, raw_request, {})
        await self.event_bus.publish("cognition.plan_generated", {"plan_id": plan.id})

        # 3. Decision choosing next best action sequence
        decision = await self.decision_engine.decide({"state": "ready"}, list(plan.tasks.keys()))
        await self.event_bus.publish("cognition.decision_made", {"decision_id": decision.id, "chosen": decision.chosen_action})

        # 4. Plan execution
        success = await self.executor.execute_plan(plan)
        
        # 5. Critic evaluation
        evaluation = await self.critic.evaluate_execution(plan)
        await self.event_bus.publish("cognition.evaluated", {"success": evaluation.success, "score": evaluation.efficiency_score})

        # 6. Reflection
        reflection = await self.reflection_engine.reflect(plan)
        await self.event_bus.publish("cognition.reflection_completed", {"lessons": reflection.lessons_learned})

        return success
