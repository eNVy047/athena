import pytest
import asyncio
from datetime import datetime
from friday.core.events import EventBus
from friday.core.cognition.models import Goal, GoalStatus, Workflow, Task, TaskStatus, ExecutionStep, Plan
from friday.core.cognition.intent_engine import IntentEngine
from friday.core.cognition.planner import Planner
from friday.core.cognition.decision_engine import DecisionEngine
from friday.core.cognition.executor import Executor
from friday.core.cognition.critic import Critic
from friday.core.cognition.reflection import ReflectionEngine
from friday.core.cognition.goal_manager import GoalManager
from friday.core.cognition.workflow_engine import WorkflowEngine
from friday.core.cognition.reasoner import Reasoner

@pytest.mark.asyncio
async def test_cognition_intent_parsing():
    engine = IntentEngine()
    engine.register_parser("test.download", lambda x: {"url": "http://test"} if "download" in x else None)
    
    intent = await engine.parse("Please download the doc")
    assert intent.name == "test.download"
    assert intent.parameters == {"url": "http://test"}
    assert intent.confidence == 1.0

@pytest.mark.asyncio
async def test_cognition_planner_plan_generation():
    planner = Planner()
    plan = await planner.generate_plan("goal123", "Download sales report and email it", {})
    assert plan.goal_id == "goal123"
    assert "task_download" in plan.tasks
    assert "task_summarize" in plan.tasks
    assert "task_email" in plan.tasks

@pytest.mark.asyncio
async def test_cognition_executor_execution():
    bus = EventBus()
    executor = Executor(bus)
    
    # Mock handlers
    execution_calls = []
    async def mock_handler(params):
        execution_calls.append(params)
        return "success_result"

    executor.register_action_handler("os.download", mock_handler)
    executor.register_action_handler("nlp.summarize", mock_handler)
    executor.register_action_handler("email.send", mock_handler)

    planner = Planner()
    plan = await planner.generate_plan("goal123", "Download report", {})
    
    success = await executor.execute_plan(plan)
    assert success is True
    assert len(execution_calls) == 3

@pytest.mark.asyncio
async def test_cognition_critic_and_reflection():
    planner = Planner()
    plan = await planner.generate_plan("goal123", "Download report", {})
    # Mock success status
    for t in plan.tasks.values():
        t.status = TaskStatus.COMPLETED

    critic = Critic()
    eval_report = await critic.evaluate_execution(plan)
    assert eval_report.success is True
    assert eval_report.efficiency_score == 1.0

    reflection_engine = ReflectionEngine()
    reflection = await reflection_engine.reflect(plan)
    assert "lessons_learned" in reflection.__dict__
    assert len(reflection.lessons_learned) > 0

@pytest.mark.asyncio
async def test_cognition_decision_making():
    engine = DecisionEngine()
    engine.add_rule("error_state", "os.recovery", 0.9)
    decision = await engine.decide({"state": "error_state"}, ["os.default"])
    assert decision.chosen_action == "os.recovery"
    assert decision.confidence == 0.9

@pytest.mark.asyncio
async def test_cognition_goal_queue_and_persistence(tmp_path):
    persistence_file = tmp_path / "goals.json"
    manager = GoalManager(str(persistence_file))
    
    goal1 = Goal(id="g1", description="Goal 1", priority=1)
    goal2 = Goal(id="g2", description="Goal 2", priority=5)
    
    manager.add_goal(goal1)
    manager.add_goal(goal2)
    
    queue = manager.get_active_queue()
    assert queue[0].id == "g2"  # Highest priority first
    
    manager.save_state()
    
    new_manager = GoalManager(str(persistence_file))
    new_manager.load_state()
    assert new_manager.get_goal("g2") is not None
    assert new_manager.get_goal("g2").priority == 5

@pytest.mark.asyncio
async def test_cognition_workflow_persistence(tmp_path):
    wf_file = tmp_path / "workflow.json"
    engine = WorkflowEngine(str(wf_file))
    
    task = Task(id="t1", name="Task 1", steps=[])
    wf = Workflow(id="w1", name="Workflow 1", tasks=[task])
    
    engine.register_workflow(wf)
    engine.save_state()
    
    new_engine = WorkflowEngine(str(wf_file))
    new_engine.load_state()
    loaded_wf = new_engine.get_workflow("w1")
    assert loaded_wf is not None
    assert loaded_wf.name == "Workflow 1"
